# Seed Math.random() with seedrandom
require('../bower_components/seedrandom/seedrandom.js') 'terra :)', global: true
# an extended custom build of lodash, generated with:
# lodash exports=commonjs include=assign,clone,filter,each,map,random,reduce,some
_ = require('../lodash_custom/lodash.custom.min.js')._

###*
# Takes a cell and returns the coordinates of its neighbors
# @param  {int} x0     - x position of cell
# @param  {int} y0     - y position of cell
# @param  {int} xMax   - maximum x index i.e. grid width
# @param  {int} yMax   - maximum x index i.e. grid height
# @param  {int} radius - (default = 1) neighbor radius
# @return {array}      - an array of [x, y] pairs of the neighboring cells
###

_.getNeighborCoordsFn = (xMax, yMax, vonNeumann, periodic) ->
  if periodic
    if vonNeumann
      # periodic von neumann
      (x0, y0, radius) ->
        coords = []
        x = undefined
        rX = undefined
        y = undefined
        rY = undefined
        rYMax = undefined
        rX = -radius
        while rX <= radius
          rYMax = radius - Math.abs(rX)
          rY = -rYMax
          while rY <= rYMax
            x = ((rX + x0) % xMax + xMax) % xMax
            y = ((rY + y0) % yMax + yMax) % yMax
            if x != x0 or y != y0
              coords.push
                x: x
                y: y
            ++rY
          ++rX
        coords
    else
      # periodic moore
      (x0, y0, radius) ->
        coords = []
        x = undefined
        xLo = undefined
        xHi = undefined
        y = undefined
        yLo = undefined
        yHi = undefined
        xLo = x0 - radius
        yLo = y0 - radius
        xHi = x0 + radius
        yHi = y0 + radius
        x = xLo
        while x <= xHi
          y = yLo
          while y <= yHi
            if x != x0 or y != y0
              coords.push
                x: (x % xMax + xMax) % xMax
                y: (y % yMax + yMax) % yMax
            ++y
          ++x
        coords
  else
    # non-periodic, need to restrict to within [0, max)
    xMax -= 1
    yMax -= 1
    if vonNeumann
      #non-periodic von-neumann
      (x0, y0, radius) ->
        coords = []
        x = undefined
        rX = undefined
        y = undefined
        rY = undefined
        rYMax = undefined
        rX = -radius
        while rX <= radius
          rYMax = radius - Math.abs(rX)
          rY = -rYMax
          while rY <= rYMax
            x = rX + x0
            y = rY + y0
            if x >= 0 and y >= 0 and x <= xMax and y <= yMax and (x != x0 or y != y0)
              coords.push
                x: x
                y: y
            ++rY
          ++rX
        coords
    else
      # non-periodic moore
      (x0, y0, radius) ->
        coords = []
        x = undefined
        xLo = undefined
        xHi = undefined
        y = undefined
        yLo = undefined
        yHi = undefined
        xLo = Math.max(0, x0 - radius)
        yLo = Math.max(0, y0 - radius)
        xHi = Math.min(x0 + radius, xMax)
        yHi = Math.min(y0 + radius, yMax)
        x = xLo
        while x <= xHi
          y = yLo
          while y <= yHi
            if x != x0 or y != y0
              coords.push
                x: x
                y: y
            ++y
          ++x
        coords

_.pickRandomWeighted = (weightedArrays) ->
  sum = 0
  rand = _.random(100, true)
  cur = undefined
  i = undefined
  i = 0
  _len = weightedArrays.length
  while i < _len
    cur = weightedArrays[i]
    sum += cur[1]
    if sum > rand
      return cur[0]
    i++
  false

###*
# CommonJS exports
# @type {Object}
###

module.exports = _
