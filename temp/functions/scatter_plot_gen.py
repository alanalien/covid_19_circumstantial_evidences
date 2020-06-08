highlight = alt.selection(type='single', on='mouseover',
                          fields=['country_name'], nearest=True)
base = alt.Chart(all_data).mark_line().encode(
    y=alt.Y('search_trend:Q'),
    x=alt.X('date:T'),
    color=alt.Color('country_name', legend=None),
    tooltip=['country_name', 'date', 'confirmed', 'death', 'recovered', 'search_trend']
)

points = base.mark_circle().encode(
    opacity=alt.value(0)
).add_selection(
    highlight
).properties(
    title="Search Trend by Date",
    width=1024,
    height=720
)

lines = base.mark_line().encode(
    color=alt.condition(highlight, 'country_name', alt.value('lightgray'), legend=None),
    size=alt.condition(highlight, alt.value(3), alt.value(1)),
    tooltip=['country_name', 'date', 'confirmed', 'death', 'recovered', 'search_trend']
)


def interactive_line (
    my_data, x_axis, y_axis, tooltip_to_add, 
    title,
    drop_na=False, drop_na_col=''  # drop na args
    ):

    ### P1: define data source
    # if dropna is required, drop na, else use the original data
    if drop_na is False:
        source = my_data
    else:
        source = my_data.drop_na(subset=[drop_na_col])

    ### P2: customize tooltip for the chart:
    base_tooltip = ['country_name', 'date', 'confirmed', 'death', 'recovered', 'active']
    my_tooltip = base_tooltip.append(tooltip_to_add)

    # create a highlight selection
    highlight = alt.selection(
        type='single',
        on='mouseover',
        fields=['country_name'],
        nearest=True)

    ### P3 make chart
    # base of the chart, defining x/y axis and the color setting
    base = alt.Chart(all_data).mark_line().encode(
        y=alt.Y('search_trend:Q'),
        x=alt.X('date:T'),
        color=alt.Color('country_name', legend=None),
        tooltip=my_tooltip
    )

    # use base info to plot a line
    lines = base.mark_line().encode(
        size=alt.condition(highlight, alt.value(1.5), alt.value(1)),
    )

    # use base info to plot transparent points for highlighting
    points = base.mark_circle().encode(
        opacity=alt.value(0)
    ).add_selection(
        highlight
    ).properties(
        title=title,
        width=250,
        height=180
    )





