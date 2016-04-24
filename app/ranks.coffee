
maxBy = require 'lodash/maxBy'

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

    truncate = (str, maxLength, suffix) ->
      if str.length > maxLength
        str = str.substring(0, maxLength + 1)
        str = str.substring(0, Math.min(str.length, str.lastIndexOf(' ')))
        str = str + suffix
      str

    svg = d3.select('body')
        .append('svg')
          .attr('width', 180000)
          .attr('height', height + margin.top + margin.bottom)
          .style('margin-left', margin.left + 'px')
        .append('g')
          .attr('transform', "translate(#{margin.left}, #{margin.top})")

    d3.json '/api/v1/computed/ranksample', (data) ->
      svg.append('g')
          .attr('class', 'x axis')
          .attr('transform', 'translate(0, 0)')

      for series, index in data
        g = svg.append('g').attr('class', 'journal')
        n_const = maxBy series.mirnas, (d) -> d[1]

        circles = g.selectAll('circle')
            .data(series.mirnas)
            .enter()
            .append('circle')
              .attr 'cx', (d, i) -> i*10
              .attr 'cy', index * 10
              .attr 'r', (d) ->
                val = Math.log(d[1]) / Math.log(n_const[1])
                if val > 0 then val * 5 else 0

module.exports = App
