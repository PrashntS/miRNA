
maxBy = require 'lodash/maxBy'
floor = require 'lodash/floor'

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
    formatYears = d3.format('0000')

    colors = ['#ffffd9', '#edf8b1', '#c7e9b4', '#7fcdbb', '#41b6c4',
              '#1d91c0', '#225ea8', '#253494', '#081d58']

    truncate = (str, maxLength, suffix) ->
      if str.length > maxLength
        str = str.substring(0, maxLength + 1)
        str = str.substring(0, Math.min(str.length, str.lastIndexOf(' ')))
        str = str + suffix
      str


    svg = d3.select('body')
        .append('svg')
          .attr('width', 1800)
          .attr('height', 1800)
          .style('margin-left', margin.left + 'px')
        .append('g')
          .attr('transform', "translate(#{margin.left}, #{margin.top})")

    filter = svg.append("defs")
      .append("filter")
        .attr("id", "blur")
      .append("feGaussianBlur")
        .attr("stdDeviation", 3)

    d3.json '/api/v1/computed/ranksample', (data) ->
      svg.append('g')
          .attr('class', 'x axis')
          .attr('transform', 'translate(0, 0)')

      for series, index in data
        g = svg.append('g').attr('class', 'journal').attr 'filter', 'url(#blur)'
        n_const = maxBy series.mirnas, (d) -> d[1]
        quantize = d3.scale.quantile().domain([0, n_const]).range(d3.range(9))

        circles = g.selectAll('circle')
            .data(series.mirnas)
            .enter()
            .append('circle')
              .attr 'cx', (d, i) -> (i % 50) * 10
              .attr 'cy', (d, i) -> floor(i, -2) / 5
              .attr 'r', (d) ->
                val = Math.log(d[1]) / Math.log(n_const[1])
                if val > 0 then val * 5 else 0
              .attr 'opacity', 0.08
              .attr 'fill', (d) ->
                val = Math.log(d[1]) / Math.log(n_const[1])
                step = 1 / colors.length
                colors[floor(floor(val, 1) / step or 0)]

module.exports = App
