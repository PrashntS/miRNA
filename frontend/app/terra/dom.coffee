# Creates an HD canvas element on page and
# returns a reference to the element

createCanvasElement = (width, height, cellSize, id, insertAfter, background) ->
  # Creates a scaled-up canvas based on the device's
  # resolution, then displays it properly using styles

  createHDCanvas = ->
    canvas = document.createElement('canvas')
    ctx = canvas.getContext('2d')
    # Creates a dummy canvas to test device's pixel ratio
    ratio = do ->
      ctx = document.createElement('canvas').getContext('2d')
      dpr = window.devicePixelRatio or 1
      bsr = (ctx.webkitBackingStorePixelRatio or
             ctx.mozBackingStorePixelRatio or
             ctx.msBackingStorePixelRatio or
             ctx.oBackingStorePixelRatio or
             ctx.backingStorePixelRatio or 1)

      dpr / bsr

    canvas.width = width * ratio
    canvas.height = height * ratio
    canvas.style.width = width + 'px'
    canvas.style.height = height + 'px'
    ctx.scale ratio, ratio
    ctx.font = 'bold ' + cellSize + 'px Arial'
    if id
      canvas.id = id
    if background
      canvas.style.background = 'rgb(' + background + ')'
    canvas

  width *= cellSize
  height *= cellSize
  canvas = createHDCanvas()

  if insertAfter
    insertAfter.parentNode.insertBefore canvas, insertAfter.nextSibling
  else
    document.body.appendChild canvas
  canvas

module.exports = createCanvasElement: createCanvasElement
