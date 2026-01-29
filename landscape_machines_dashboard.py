#!/usr/bin/env python3
"""
🏢 Landscape Infrastructure Dashboard PRO
Ultra-professional corporate machine inventory with full annotations support
"""

import streamlit as st
import json
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from landscape_api.base import API
from datetime import datetime
from typing import List, Dict, Any, Tuple
from collections import Counter

# ============================================================================
# PAGE CONFIG & STYLING
# ============================================================================

st.set_page_config(
    page_title="Landscape Infrastructure Dashboard",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional styling
st.markdown("""
<style>
    /* Main theme */
    :root {
        --primary: #1f77b4;
        --secondary: #ff7f0e;
        --success: #2ca02c;
        --danger: #d62728;
        --warning: #ff9800;
        --info: #17a2b8;
    }

    /* Header styling */
    .dashboard-header {
        background: linear-gradient(135deg, #1f77b4 0%, #0d47a1 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 4px 15px rgba(31, 119, 180, 0.3);
    }

    .dashboard-title {
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }

    .dashboard-subtitle {
        font-size: 1rem;
        opacity: 0.9;
        margin: 0.5rem 0 0 0;
    }

    /* Annotation tags */
    .annotation-key {
        display: inline-block;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 0.4rem 0.8rem;
        border-radius: 15px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-right: 0.5rem;
        margin-bottom: 0.5rem;
        box-shadow: 0 2px 4px rgba(102, 126, 234, 0.3);
    }

    .annotation-value {
        display: inline-block;
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 0.3rem 0.7rem;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 500;
        margin-left: 0.3rem;
    }

    .status-badge {
        display: inline-block;
        padding: 0.4rem 0.8rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
    }

    .status-active {
        background-color: #d4edda;
        color: #155724;
    }

    .status-inactive {
        background-color: #f8d7da;
        color: #721c24;
    }

    .annotation-card {
        background: white;
        border-left: 4px solid #667eea;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }

    .metric-card {
        background: white;
        border-left: 4px solid #1f77b4;
        padding: 1.5rem;
        border-radius: 8px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
    }

    .metric-card:hover {
        box-shadow: 0 4px 16px rgba(0,0,0,0.15);
        transform: translateY(-2px);
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# API & CACHING
# ============================================================================

@st.cache_resource
def init_api():
    """Initialize Landscape API connection."""
    import os
    return API(
        uri=os.getenv("LANDSCAPE_API_URI", "https://landscape.example.com/api/"),
        access_key=os.getenv("LANDSCAPE_API_KEY", "YOUR_API_KEY_HERE"),
        secret_key=os.getenv("LANDSCAPE_API_SECRET", "YOUR_API_SECRET_HERE"),
        ssl_ca_file=None,
        json=True
    )


def parse_json_response(response: Any) -> Any:
    """Parse JSON string response if needed."""
    if isinstance(response, str):
        return json.loads(response)
    return response


@st.cache_data(ttl=300)
def get_all_machines_with_annotations() -> List[Dict]:
    """Fetch all machines with full annotations from Landscape API."""
    try:
        api = init_api()
        # Fetch with_annotations=True to get all annotation data
        computers_response = api.get_computers(query="tag:ALL", limit=300, with_annotations=True)
        computers = parse_json_response(computers_response)
        return computers if isinstance(computers, list) else [computers]
    except Exception as e:
        st.error(f"❌ Error fetching machines: {str(e)}")
        return []


# ============================================================================
# DATA EXTRACTION & PROCESSING
# ============================================================================

def extract_all_tags(machines: List[Dict]) -> List[str]:
    """Extract unique tags from all machines."""
    tags_set = set()
    for machine in machines:
        tags = machine.get('tags', [])
        if isinstance(tags, list):
            tags_set.update(tags)
    return sorted(list(tags_set))


def extract_all_annotations(machines: List[Dict]) -> Dict[str, set]:
    """Extract all unique annotation keys and values."""
    annotations_dict = {}
    for machine in machines:
        annotations = machine.get('annotations', {})
        if isinstance(annotations, dict):
            for key, value in annotations.items():
                if key not in annotations_dict:
                    annotations_dict[key] = set()
                annotations_dict[key].add(str(value))
    return annotations_dict


def categorize_tags(tags: List[str]) -> Dict[str, List[str]]:
    """Categorize tags into logical groups."""

    # Define specific team tags
    team_tags = {
        'Engineering', 'SysAdmin', 'EarlyAdopters', 'CustomerServices',
        'Profitability management', 'Corporate Security'
    }

    # Define location tags - all cities and ALL
    location_tags = [
        'ALL', 'Sarajevo', 'Zagreb', 'Belgrade', 'Belgrad',
        'Bogota', 'Curitiba', 'Dublin', 'Katowice', 'Kosice'
    ]

    categories = {
        '📍 Locations': [],
        '👥 Teams': [],
        '🏷️ Other': []
    }

    for tag in tags:
        tag_lower = tag.lower()

        # Check for exact team tags (case-insensitive match)
        if any(tag.lower() == team.lower() for team in team_tags):
            categories['👥 Teams'].append(tag)
        # Check for location tags (exact match first)
        elif any(tag.lower() == loc.lower() for loc in location_tags):
            categories['📍 Locations'].append(tag)
        # Check if tag looks like a location (Title Case and not in teams or known categories)
        elif tag and tag[0].isupper() and tag_lower not in [t.lower() for t in team_tags] and len(tag) > 2:
            # If tag is Title Case and not a known team tag, likely a location/city
            categories['📍 Locations'].append(tag)
        else:
            # Everything else: System tags, Services, and other tags
            categories['🏷️ Other'].append(tag)

    # Sort each category
    for key in categories:
        categories[key] = sorted(categories[key])

    return {k: v for k, v in categories.items() if v}


def get_machine_status(machine: Dict) -> Tuple[str, str]:
    """Determine machine status - offline if not pinged in 24+ hours."""
    last_ping = machine.get('last_ping_time', '')

    if 'never' in str(last_ping).lower() or not last_ping:
        return '⚠️ Offline', 'status-inactive'

    try:
        # Parse the timestamp (format: 2026-01-20T12:43:32Z)
        ping_time = datetime.fromisoformat(str(last_ping).replace('Z', '+00:00'))
        ping_time = ping_time.replace(tzinfo=None)  # Make it naive for comparison

        # Check if last ping is older than 24 hours (1440 minutes)
        minutes_since_ping = (datetime.now() - ping_time).total_seconds() / 60

        if minutes_since_ping > 1440:  # 24 hours
            return '⚠️ Offline', 'status-inactive'
    except:
        pass

    return '✅ Online', 'status-active'


def filter_machines(
    machines: List[Dict],
    selected_tags: List[str],
    selected_annotations: Dict[str, List[str]],
    search_text: str = ""
) -> List[Dict]:
    """Filter machines by tags, annotations, and search text."""
    filtered = machines.copy()

    # Filter by tags
    if selected_tags:
        filtered = [
            m for m in filtered
            if any(tag in m.get('tags', []) for tag in selected_tags)
        ]

    # Filter by annotations
    if selected_annotations:
        for ann_key, ann_values in selected_annotations.items():
            if ann_values:
                filtered = [
                    m for m in filtered
                    if str(m.get('annotations', {}).get(ann_key, '')) in ann_values
                ]

    # Filter by search text
    if search_text:
        search_lower = search_text.lower()
        filtered = [
            m for m in filtered
            if (search_lower in m.get('hostname', '').lower() or
                search_lower in str(m.get('id', '')).lower() or
                any(search_lower in str(v).lower() for v in m.get('annotations', {}).values()))
        ]

    return filtered


# ============================================================================
# MAIN DASHBOARD
# ============================================================================

# Header
st.markdown("""
<div class="dashboard-header">
    <h1 class="dashboard-title">🏢 Landscape Infrastructure Dashboard PRO</h1>
    <p class="dashboard-subtitle">Enterprise-grade machine inventory with full annotations & tags support</p>
</div>
""", unsafe_allow_html=True)

# Load data
machines = get_all_machines_with_annotations()
total_machines = len(machines)

if not machines:
    st.error("❌ Could not fetch machines from Landscape API")
    st.stop()

# Extract data
all_tags = extract_all_tags(machines)
all_annotations = extract_all_annotations(machines)
tag_categories = categorize_tags(all_tags)

# ============================================================================
# SIDEBAR - ADVANCED FILTERS
# ============================================================================

st.sidebar.markdown("### 🔍 ADVANCED FILTERS")
st.sidebar.markdown("---")

# Search box
search_input = st.sidebar.text_input(
    "🔎 Search",
    placeholder="Hostname, annotation value...",
    help="Search by hostname or annotation values"
)

st.sidebar.markdown("---")

# Tag filters
st.sidebar.markdown("### 🏷️ FILTER BY TAGS")
selected_tags = []

for category, tags in tag_categories.items():
    with st.sidebar.expander(f"{category} ({len(tags)})"):
        category_tags = st.multiselect(
            f"Select {category.lower()}:",
            options=tags,
            default=[],
            key=f"category_{category}"
        )
        selected_tags.extend(category_tags)

st.sidebar.markdown("---")

# Annotation filters
st.sidebar.markdown("### 📝 FILTER BY ANNOTATIONS")
selected_annotations = {}

annotation_keys = sorted(all_annotations.keys())

if annotation_keys:
    with st.sidebar.expander("🔧 Annotation Keys"):
        for ann_key in annotation_keys[:20]:  # Show top 20 for performance
            values = sorted(list(all_annotations[ann_key]))
            selected_values = st.multiselect(
                f"**{ann_key}**:",
                options=values,
                default=[],
                key=f"annotation_{ann_key}",
                max_selections=5
            )
            if selected_values:
                selected_annotations[ann_key] = selected_values
else:
    st.sidebar.info("No annotations found")

st.sidebar.markdown("---")

# Metrics
col1, col2 = st.sidebar.columns(2)
with col1:
    st.metric("📊 Total", total_machines)
with col2:
    st.metric("📝 Annotations", len(all_annotations))

# Apply filters
filtered_machines = filter_machines(machines, selected_tags, selected_annotations, search_input)

# Initialize session state for status filter
if 'status_filter' not in st.session_state:
    st.session_state.status_filter = 'All'

# ============================================================================
# TOP METRICS
# ============================================================================

st.markdown("### 📊 INFRASTRUCTURE OVERVIEW")

# Calculate online/offline counts
online_count = 0
offline_count = 0

for m in filtered_machines:
    status, _ = get_machine_status(m)
    if '✅' in status:
        online_count += 1
    else:
        offline_count += 1

# Status filter buttons
col_status1, col_status2, col_status3, col_status_spacer = st.columns([1.5, 1.5, 1.5, 5])

with col_status1:
    if st.button(f"🎯 All ({len(filtered_machines)})", key="btn_all_status", use_container_width=True):
        st.session_state.status_filter = 'All'

with col_status2:
    if st.button(f"✅ Online ({online_count})", key="btn_online_status", use_container_width=True):
        st.session_state.status_filter = 'Online'

with col_status3:
    if st.button(f"⚠️ Offline ({offline_count})", key="btn_offline_status", use_container_width=True):
        st.session_state.status_filter = 'Offline'

# Apply status filter
if st.session_state.status_filter == 'Online':
    filtered_machines = [m for m in filtered_machines if '✅' in get_machine_status(m)[0]]
    online_count = len(filtered_machines)
    offline_count = 0
elif st.session_state.status_filter == 'Offline':
    filtered_machines = [m for m in filtered_machines if '⚠️' in get_machine_status(m)[0]]
    offline_count = len(filtered_machines)
    online_count = 0

# Display current filter status
if st.session_state.status_filter != 'All':
    st.info(f"📌 Filtered by: **{st.session_state.status_filter}** status")

st.markdown("---")

# Metrics display
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("🎯 Filtered", len(filtered_machines), f"{(len(filtered_machines)/total_machines*100):.1f}%")

with col2:
    st.metric("✅ Online", online_count)

with col3:
    st.metric("⚠️ Offline", offline_count)

with col4:
    st.metric("🔧 Distributions", len(set(m.get('distribution', 'N/A') for m in filtered_machines)))

with col5:
    if filtered_machines:
        avg_tags = sum(len(m.get('tags', [])) for m in filtered_machines) / len(filtered_machines)
        st.metric("🏷️ Avg Tags", f"{avg_tags:.1f}")

st.markdown("---")

# ============================================================================
# RESULTS TABS
# ============================================================================

if len(filtered_machines) == 0:
    st.warning("🔍 No machines match your filters. Try adjusting your search criteria.")
else:
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📋 Machines",
        "📊 Analytics",
        "🔖 Tags",
        "📝 Annotations",
        "💾 Export"
    ])

    # ====================================================================
    # TAB 1: MACHINES TABLE
    # ====================================================================
    with tab1:
        st.markdown("### 🖥️ MACHINE INVENTORY")

        rows = []
        for machine in filtered_machines:
            hostname = machine.get('hostname', 'N/A').strip()
            machine_id = machine.get('id', '')
            tags = machine.get('tags', [])
            distribution = machine.get('distribution', 'N/A')
            last_ping = machine.get('last_ping_time', 'Never')
            status, _ = get_machine_status(machine)
            annotations = machine.get('annotations', {})

            rows.append({
                'ID': machine_id,
                'Hostname': hostname,
                'Status': status,
                'Distribution': distribution,
                'Tags': len(tags),
                'Annotations': len(annotations),
                'Last Ping': last_ping,
            })

        df = pd.DataFrame(rows)

        st.dataframe(
            df,
            use_container_width=True,
            height=min(len(df) * 35 + 50, 700)
        )

        # Expandable machine details
        st.markdown("### 🔍 MACHINE DETAILS")

        selected_machine_id = st.selectbox(
            "Select machine to view details:",
            options=[m['ID'] for m in rows],
            format_func=lambda x: f"ID {x} - {next((m['Hostname'] for m in rows if m['ID'] == x), 'N/A')}"
        )

        if selected_machine_id:
            selected_machine = next(m for m in filtered_machines if m['id'] == selected_machine_id)

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("#### 🏷️ TAGS")
                tags = selected_machine.get('tags', [])
                if tags:
                    for tag in tags[:20]:
                        st.markdown(f"🔹 `{tag}`")
                    if len(tags) > 20:
                        st.info(f"... and {len(tags)-20} more tags")
                else:
                    st.info("No tags")

            with col2:
                st.markdown("#### 📝 ANNOTATIONS")
                annotations = selected_machine.get('annotations', {})
                if annotations:
                    for key, value in list(annotations.items())[:15]:
                        st.markdown(f"**{key}**: `{value}`")
                    if len(annotations) > 15:
                        st.info(f"... and {len(annotations)-15} more annotations")
                else:
                    st.info("No annotations")

    # ====================================================================
    # TAB 2: ANALYTICS - MONITORING DASHBOARD
    # ====================================================================
    with tab2:
        st.markdown("### 📊 MONITORING DASHBOARD")
        st.markdown("---")

        # Initialize session state for annotation filters
        if 'ann_filter' not in st.session_state:
            st.session_state.ann_filter = {}

        # Function to get annotation value counts
        def get_annotation_stats(machines, exclude_keys=None):
            """Get stats for annotations with limited unique values"""
            if exclude_keys is None:
                exclude_keys = []

            ann_stats = {}
            for machine in machines:
                annotations = machine.get('annotations', {})
                for key, value in annotations.items():
                    if key in exclude_keys:
                        continue
                    if key not in ann_stats:
                        ann_stats[key] = Counter()
                    ann_stats[key][str(value)] += 1

            # Filter to only annotations with < 10 unique values
            filtered_stats = {}
            for key, value_counts in ann_stats.items():
                if len(value_counts) < 10:  # Only show if < 10 unique values
                    filtered_stats[key] = value_counts

            return filtered_stats

        # Exclude these annotations (they have 30+ different values)
        exclude_annotations = ['luks_key_exp_date', 'disk_usage', 'date', 'timestamp', 'expire', 'expiration']

        ann_stats = get_annotation_stats(filtered_machines, exclude_annotations)

        # Display base KPIs in first row
        kpi_cols = st.columns(4)
        kpi_data = [
            ('Total Machines', len(filtered_machines), '#667eea', '#764ba2'),
            ('Online', online_count, '#2ca02c', '#1f771f'),
            ('Offline', offline_count, '#d62728', '#8b0000'),
            ('Annotations', len(all_annotations), '#ff9500', '#ff6b6b')
        ]

        for idx, (label, value, color1, color2) in enumerate(kpi_data):
            with kpi_cols[idx]:
                if label == 'Online':
                    pct = (value / len(filtered_machines) * 100) if filtered_machines else 0
                    st.markdown(f"""
                    <div style="background: linear-gradient(135deg, {color1} 0%, {color2} 100%); padding: 20px; border-radius: 10px; text-align: center; color: white; cursor: pointer;">
                        <h3 style="margin: 0; font-size: 14px; opacity: 0.9;">{label}</h3>
                        <h1 style="margin: 10px 0 0 0; font-size: 32px;">{value}</h1>
                        <p style="margin: 5px 0 0 0; font-size: 12px;">{pct:.1f}%</p>
                    </div>
                    """, unsafe_allow_html=True)
                elif label == 'Offline':
                    pct = (value / len(filtered_machines) * 100) if filtered_machines else 0
                    st.markdown(f"""
                    <div style="background: linear-gradient(135deg, {color1} 0%, {color2} 100%); padding: 20px; border-radius: 10px; text-align: center; color: white; cursor: pointer;">
                        <h3 style="margin: 0; font-size: 14px; opacity: 0.9;">{label}</h3>
                        <h1 style="margin: 10px 0 0 0; font-size: 32px;">{value}</h1>
                        <p style="margin: 5px 0 0 0; font-size: 12px;">{pct:.1f}%</p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div style="background: linear-gradient(135deg, {color1} 0%, {color2} 100%); padding: 20px; border-radius: 10px; text-align: center; color: white;">
                        <h3 style="margin: 0; font-size: 14px; opacity: 0.9;">{label}</h3>
                        <h1 style="margin: 10px 0 0 0; font-size: 32px;">{value}</h1>
                    </div>
                    """, unsafe_allow_html=True)

        st.markdown("---")

        # Dynamic Annotation KPI Cards
        if ann_stats:
            st.markdown("### 🏷️ ANNOTATION MONITORING CARDS")

            # Create dynamic grid for annotation KPIs
            annotation_kpi_list = list(ann_stats.items())

            # Show annotations in rows of 4 columns
            for i in range(0, len(annotation_kpi_list), 4):
                cols = st.columns(4)
                for col_idx, col in enumerate(cols):
                    if i + col_idx < len(annotation_kpi_list):
                        ann_key, value_counts = annotation_kpi_list[i + col_idx]
                        top_value = value_counts.most_common(1)[0]  # Get most common value
                        top_value_name, top_value_count = top_value

                        with col:
                            # Create button-like KPI card
                            if st.button(f"📊 {ann_key}", key=f"btn_ann_{ann_key}"):
                                st.session_state.ann_filter['key'] = ann_key
                                st.session_state.ann_filter['show'] = True

                            # Display all values for this annotation
                            st.markdown(f"""
                            <div style="background: linear-gradient(135deg, #17a2b8 0%, #138496 100%); padding: 15px; border-radius: 8px; text-align: center; color: white; margin-top: 10px; font-size: 12px;">
                                <b style="font-size: 11px; opacity: 0.9;">Most Common:</b><br>
                                <span style="font-size: 14px;">{top_value_name}</span><br>
                                <span style="font-size: 13px; opacity: 0.8;">({top_value_count} machines)</span><br><br>
                                <span style="opacity: 0.7; font-size: 10px;">{len(value_counts)} variants</span>
                            </div>
                            """, unsafe_allow_html=True)

            st.markdown("---")

        # Show selected annotation details
        if st.session_state.ann_filter.get('show') and st.session_state.ann_filter.get('key') in ann_stats:
            selected_ann_key = st.session_state.ann_filter['key']
            selected_ann_values = ann_stats[selected_ann_key]

            st.markdown(f"### 📋 {selected_ann_key} - Value Breakdown")

            # Create value tabs
            value_tabs = st.tabs([f"{v} ({c})" for v, c in selected_ann_values.most_common()])

            for tab_idx, (tab, (value_name, count)) in enumerate(zip(value_tabs, selected_ann_values.most_common())):
                with tab:
                    st.markdown(f"**Value:** `{value_name}` | **Count:** {count} machines")

                    # Show machines with this value
                    machines_with_value = [m for m in filtered_machines
                                         if m.get('annotations', {}).get(selected_ann_key) == value_name]

                    if machines_with_value:
                        machines_table = []
                        for m in machines_with_value:
                            machines_table.append({
                                'Hostname': m.get('hostname', 'N/A'),
                                'Status': '✅ Online' if '✅' in get_machine_status(m)[0] else '⚠️ Offline',
                                'Distribution': m.get('distribution', 'N/A'),
                                'Tags': ', '.join(m.get('tags', [])[:3]) + ('...' if len(m.get('tags', [])) > 3 else '')
                            })

                        st.dataframe(pd.DataFrame(machines_table), use_container_width=True, hide_index=True)
                    else:
                        st.info("No machines found")

            if st.button("❌ Close Details", key="close_ann_details"):
                st.session_state.ann_filter = {}
                st.rerun()

        st.markdown("---")

        # Row 1: Status and Distribution
        col1, col2 = st.columns(2)

        with col1:
            status_data = {'Online': online_count, 'Offline': offline_count}
            fig1 = go.Figure(data=[go.Pie(
                labels=list(status_data.keys()),
                values=list(status_data.values()),
                marker=dict(colors=['#2ca02c', '#d62728']),
                textposition='inside',
                textinfo='label+percent+value',
                hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>'
            )])
            fig1.update_layout(title="Machine Status Distribution", height=450, showlegend=True, font=dict(size=12))
            st.plotly_chart(fig1, use_container_width=True)

        with col2:
            dist_counts = Counter(m.get('distribution', 'Unknown') for m in filtered_machines)
            dist_df = pd.DataFrame(list(dist_counts.items()), columns=['Distribution', 'Count']).sort_values('Count', ascending=False)
            fig2 = px.bar(dist_df, x='Distribution', y='Count', title="OS Distribution",
                         color='Count', color_continuous_scale='Blues', height=450,
                         labels={'Count': 'Number of Machines'},
                         hover_data={'Count': True})
            fig2.update_layout(hovermode='x unified')
            st.plotly_chart(fig2, use_container_width=True)

        st.markdown("---")

        # Row 2: Annotation Keys Analytics
        st.markdown("### 📝 ANNOTATION KEYS ANALYTICS")

        col3, col4 = st.columns(2)

        with col3:
            all_annotation_keys = []
            for m in filtered_machines:
                all_annotation_keys.extend(m.get('annotations', {}).keys())

            ann_key_counts = Counter(all_annotation_keys)
            top_ann_keys = dict(sorted(ann_key_counts.items(), key=lambda x: x[1], reverse=True)[:15])

            if top_ann_keys:
                ann_keys_df = pd.DataFrame({
                    'Key': list(top_ann_keys.keys()),
                    'Count': list(top_ann_keys.values())
                }).sort_values('Count', ascending=True)

                fig3 = px.bar(
                    ann_keys_df,
                    x='Count',
                    y='Key',
                    orientation='h',
                    title="Top 15 Annotation Keys (Most Common)",
                    color='Count',
                    color_continuous_scale='Viridis',
                    height=500,
                    labels={'Count': 'Number of Machines', 'Key': 'Annotation Key'}
                )
                fig3.update_layout(
                    xaxis_title="Number of Machines",
                    yaxis_title="Annotation Key",
                    showlegend=False,
                    hovermode='closest',
                    font=dict(size=11)
                )
                st.plotly_chart(fig3, use_container_width=True)
            else:
                st.info("No annotations available in filtered machines")

        with col4:
            # Annotation values per key - heatmap style
            if all_annotation_keys:
                st.markdown("#### Top 10 Annotation Keys with Value Distribution")

                top_keys_for_heatmap = dict(sorted(ann_key_counts.items(), key=lambda x: x[1], reverse=True)[:10])

                heatmap_data = []
                for key in top_keys_for_heatmap.keys():
                    value_counts = Counter()
                    for m in filtered_machines:
                        annotations = m.get('annotations', {})
                        if key in annotations:
                            value_counts[str(annotations[key])] += 1

                    top_values = dict(sorted(value_counts.items(), key=lambda x: x[1], reverse=True)[:5])
                    for value, count in top_values.items():
                        heatmap_data.append({'Key': key, 'Value': value[:20], 'Count': count})

                if heatmap_data:
                    heatmap_df = pd.DataFrame(heatmap_data)
                    fig_heatmap = px.bar(
                        heatmap_df,
                        x='Value',
                        y='Key',
                        color='Count',
                        orientation='h',
                        color_continuous_scale='RdYlGn',
                        height=500,
                        title="Annotation Key-Value Distribution",
                        labels={'Count': 'Occurrences', 'Key': 'Annotation Key', 'Value': 'Value (truncated)'}
                    )
                    fig_heatmap.update_layout(hovermode='closest')
                    st.plotly_chart(fig_heatmap, use_container_width=True)

        st.markdown("---")

        # Row 3: Tags Analytics
        st.markdown("### 🏷️ TAGS ANALYTICS")

        col5, col6 = st.columns(2)

        with col5:
            all_tags_filtered = []
            for m in filtered_machines:
                all_tags_filtered.extend(m.get('tags', []))

            tag_counts = Counter(all_tags_filtered)
            top_tags = dict(sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:12])

            if top_tags:
                tags_df = pd.DataFrame({
                    'Tag': list(top_tags.keys()),
                    'Count': list(top_tags.values())
                }).sort_values('Count', ascending=True)

                fig4 = px.bar(
                    tags_df,
                    x='Count',
                    y='Tag',
                    orientation='h',
                    title="Top 12 Tags Distribution",
                    color='Count',
                    color_continuous_scale='Sunset',
                    height=450,
                    labels={'Count': 'Number of Machines', 'Tag': 'Tag'}
                )
                fig4.update_layout(
                    xaxis_title="Number of Machines",
                    yaxis_title="Tag",
                    showlegend=False,
                    hovermode='closest'
                )
                st.plotly_chart(fig4, use_container_width=True)

        with col6:
            if top_tags:
                fig5 = go.Figure(data=[go.Pie(
                    labels=list(top_tags.keys()),
                    values=list(top_tags.values()),
                    hole=0.4,
                    marker=dict(colors=px.colors.qualitative.Pastel),
                    textposition='auto',
                    hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>'
                )])
                fig5.update_layout(title="Tags Distribution (Donut)", height=450, font=dict(size=11))
                st.plotly_chart(fig5, use_container_width=True)

    # ====================================================================
    # TAB 3: TAGS BREAKDOWN
    # ====================================================================
    with tab3:
        st.markdown("### 🏷️ TAGS DETAILED BREAKDOWN")

        for category, tags in tag_categories.items():
            with st.expander(f"{category} - {len(tags)} tags", expanded=True):
                tag_stats = []
                for tag in sorted(tags):
                    count = sum(1 for m in filtered_machines if tag in m.get('tags', []))
                    tag_stats.append({'Tag': tag, 'Count': count, 'Percentage': f"{(count/len(filtered_machines)*100):.1f}%"})

                tag_stats_df = pd.DataFrame(tag_stats).sort_values('Count', ascending=False)
                st.dataframe(tag_stats_df, use_container_width=True, hide_index=True)

    # ====================================================================
    # TAB 4: ANNOTATIONS BREAKDOWN
    # ====================================================================
    with tab4:
        st.markdown("### 📝 ANNOTATIONS DETAILED BREAKDOWN")

        # Show all annotation keys used in filtered machines
        filtered_annotation_keys = {}
        for machine in filtered_machines:
            annotations = machine.get('annotations', {})
            for key, value in annotations.items():
                if key not in filtered_annotation_keys:
                    filtered_annotation_keys[key] = Counter()
                filtered_annotation_keys[key][str(value)] += 1

        if filtered_annotation_keys:
            for ann_key in sorted(filtered_annotation_keys.keys())[:30]:
                with st.expander(f"📌 **{ann_key}** ({len(filtered_annotation_keys[ann_key])} unique values)", expanded=False):
                    values_df = pd.DataFrame(
                        [{'Value': v, 'Count': c, 'Percentage': f"{(c/len(filtered_machines)*100):.1f}%"}
                         for v, c in filtered_annotation_keys[ann_key].most_common(10)],
                    )

                    col1, col2 = st.columns([2, 1])

                    with col1:
                        st.dataframe(values_df, use_container_width=True, hide_index=True)

                    with col2:
                        if len(values_df) > 0:
                            fig = px.pie(values_df, values='Count', names='Value',
                                       title=f"{ann_key} Distribution")
                            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No annotations in filtered machines")

    # ====================================================================
    # TAB 5: EXPORT
    # ====================================================================
    with tab5:
        st.markdown("### 💾 EXPORT DATA")

        col1, col2, col3 = st.columns(3)

        # CSV Export
        with col1:
            rows = []
            for machine in filtered_machines:
                rows.append({
                    'ID': machine.get('id', ''),
                    'Hostname': machine.get('hostname', 'N/A').strip(),
                    'Distribution': machine.get('distribution', 'N/A'),
                    'Tags': ', '.join(machine.get('tags', [])),
                    'Last Ping': machine.get('last_ping_time', 'Never'),
                })

            df_export = pd.DataFrame(rows)
            csv_data = df_export.to_csv(index=False)

            st.download_button(
                label="📥 CSV Report",
                data=csv_data,
                file_name=f"landscape_machines_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )

        # JSON Export
        with col2:
            json_data = json.dumps(filtered_machines, indent=2, default=str)
            st.download_button(
                label="📥 JSON Export",
                data=json_data,
                file_name=f"landscape_machines_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )

        # Summary
        with col3:
            summary = {
                'export_date': datetime.now().isoformat(),
                'total_machines': len(filtered_machines),
                'online_machines': online_count,
                'offline_machines': offline_count,
                'unique_tags': len(all_tags),
                'unique_annotations': len(all_annotations),
            }

            summary_json = json.dumps(summary, indent=2)
            st.download_button(
                label="📋 Summary",
                data=summary_json,
                file_name=f"landscape_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")

footer_col1, footer_col2, footer_col3 = st.columns([1, 2, 1])

with footer_col1:
    st.markdown(f"**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

with footer_col2:
    st.markdown(f"**Status:** 🟢 API Connected | **Machines:** {total_machines} | **Filtered:** {len(filtered_machines)}")

with footer_col3:
    st.markdown(f"**Tags:** {len(all_tags)} | **Annotations:** {len(all_annotations)}")
