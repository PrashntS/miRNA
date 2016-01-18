_ = require('./util')

module.exports = (canvas, grid, cellSize, trails, background) ->
  ctx = canvas.getContext('2d')
  if trails and background
    ctx.fillStyle = 'rgba(' + background + ',' + 1 - trails + ')'
    ctx.fillRect 0, 0, canvas.width, canvas.height
  else if trails
    console.err 'Background must also be set for trails'
    return
  else
    ctx.clearRect 0, 0, canvas.width, canvas.height
  _.each grid, (column, x) ->
    _.each column, (creature, y) ->
      if creature
        color = if creature.colorFn then creature.colorFn() else
          "#{creature.color}"#,#{creature.energy / creature.maxEnergy}"

        ctx.fillStyle = 'rgb(' + color + ')'

        if creature.character
          ctx.fillText creature.character, x * cellSize, y * cellSize + cellSize
        else
          ctx.fillRect x * cellSize, y * cellSize, cellSize, cellSize
