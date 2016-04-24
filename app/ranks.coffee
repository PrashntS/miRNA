
App =
  init: ->
    margin =
      top: 20
      right: 200
      bottom: 0
      left: 20
    width = 800
    height = 650
    start_year = 1970
    end_year = 2013
    c = d3.scale.category20c()
    x = d3.scale.linear().range([
      0
      width
    ])
    xAxis = d3.svg.axis().scale(x).orient('top')
    formatYears = d3.format('0000')

    truncate = (str, maxLength, suffix) ->
      if str.length > maxLength
        str = str.substring(0, maxLength + 1)
        str = str.substring(0, Math.min(str.length, str.lastIndexOf(' ')))
        str = str + suffix
      str

    xAxis.tickFormat formatYears
    svg = d3.select('body').append('svg').attr('width', width + margin.left + margin.right).attr('height', height + margin.top + margin.bottom).style('margin-left', margin.left + 'px').append('g').attr('transform', 'translate(' + margin.left + ',' + margin.top + ')')
    d3.json '/api/v1/computed/ranksample', (data) ->

      mouseover = (p) ->
        g = d3.select(this).node().parentNode
        d3.select(g).selectAll('circle').style 'display', 'none'
        d3.select(g).selectAll('text.value').style 'display', 'block'
        return

      mouseout = (p) ->
        g = d3.select(this).node().parentNode
        d3.select(g).selectAll('circle').style 'display', 'block'
        d3.select(g).selectAll('text.value').style 'display', 'none'
        return

      x.domain [
        start_year
        end_year
      ]
      xScale = d3.scale.linear().domain([
        start_year
        end_year
      ]).range([
        0
        width
      ])
      svg.append('g').attr('class', 'x axis').attr('transform', 'translate(0,' + 0 + ')').call xAxis
      j = 0
      while j < data.length
        g = svg.append('g').attr('class', 'journal')
        circles = g.selectAll('circle').data(data[j]['articles']).enter().append('circle')
        text = g.selectAll('text').data(data[j]['articles']).enter().append('text')
        rScale = d3.scale.linear().domain([
          0
          d3.max(data[j]['articles'], (d) ->
            d[1]
          )
        ]).range([
          2
          9
        ])
        circles.attr('cx', (d, i) ->
          xScale d[0]
        ).attr('cy', j * 20 + 20).attr('r', (d) ->
          rScale d[1]
        ).style 'fill', (d) ->
          c j
        text.attr('y', j * 20 + 25).attr('x', (d, i) ->
          xScale(d[0]) - 5
        ).attr('class', 'value').text((d) ->
          d[1]
        ).style('fill', (d) ->
          c j
        ).style 'display', 'none'
        g.append('text').attr('y', j * 20 + 25).attr('x', width + 20).attr('class', 'label').text(truncate(data[j]['name'], 30, '...')).style('fill', (d) ->
          c j
        ).on('mouseover', mouseover).on 'mouseout', mouseout
        j++
      return


module.exports = App
