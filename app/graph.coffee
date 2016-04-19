
jquery = require 'jquery'

App =
  init: ->
    colors = d3.scale.category20()

    jquery.get '/api/rank/computedfunctions'
      .done (dat) ->
        nv.addGraph ->
          # chart = nv.models.lineWithFocusChart()
          # chart.xAxis.showMaxMin(false).tickFormat((d) -> dat.xTicks[d])
          # chart.x2Axis.ticks(false)
          # chart.yAxis.tickFormat d3.format(',.2f')
          # chart.y2Axis.tickFormat d3.format(',.2f')
          # d3.select('#chart svg')
          #   .datum(dat.data)
          #   .transition().duration(500)
          #   .call chart
          # nv.utils.windowResize chart.update
          # chart

          nv.addGraph ->
            chart = nv.models.stackedAreaChart()
                .useInteractiveGuideline(true)
                .x((d) -> d[2])
                .y((d) -> d[1])
                .duration(300)

            chart.xAxis
                .tickValues ->
                  dat[0].values
                .tickFormat (d) ->
                  console.log d
                  d[0] or dat[0].values[d][0]

            d3.select('#chart svg')
                .datum(dat)
                .transition()
                .duration(1000)
                .call chart
            nv.utils.windowResize chart.update
            chart


module.exports = App
