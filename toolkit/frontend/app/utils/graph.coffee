class Graph
  constructor: (opts) ->
    {@w, @h, elem} = opts
    @color = d3.scale.category10()
    @initZoomAndPan()
    @svg = d3.select elem
      .append 'svg:svg'
        .attr 'width', @w
        .attr 'height', @h
        .attr 'id', 'svg'
        .attr 'pointer-events', 'all'
        .attr 'viewBox', "0 0 #{@w} #{@h}"
        .attr 'perserveAspectRatio', 'xMinYMid'
      .call @zoom

    @vis = @svg.append 'svg:g'
    @initDefs()

    @force = d3.layout.force()
    @nodes = @force.nodes()
    @links = @force.links()

  addNode: (id) ->
    @nodes.push 'id': id

  initZoomAndPan: ->
    @zoom = d3.behavior.zoom()
      .scaleExtent [1, 10]
      .on "zoom", =>
        @vis.attr "transform",
          "translate(#{d3.event.translate}) scale(#{d3.event.scale})"

    @drag = d3.behavior.drag()
      .origin (d) -> d
      .on "dragstart", (d) ->
        d3.event.sourceEvent.stopPropagation()
        d3.select(@).classed "dragging", true
      .on "drag", (d) ->
        d3.select(@)
          .attr "cx", d.x = d3.event.x
          .attr "cy", d.y = d3.event.y
      .on "dragend", (d) ->
        d3.select(@).classed "dragging", false

  initDefs: ->
    @svg.append('svg:defs').append('svg:marker')
        .attr('id', 'end-arrow')
        .attr('viewBox', '0 -5 10 10')
        .attr('refX', 6)
        .attr('markerWidth', 3)
        .attr('markerHeight', 3)
        .attr('orient', 'auto')
      .append('svg:path')
        .attr('d', 'M0,-5L10,0L0,5')
        .attr('fill', '#000')

    @svg.append('svg:defs').append('svg:marker')
        .attr('id', 'start-arrow')
        .attr('viewBox', '0 -5 10 10')
        .attr('refX', 10)
        .attr('markerWidth', 5)
        .attr('markerHeight', 5)
        .attr('orient', 'auto')
      .append('svg:path')
        .attr('d', 'M0,-5L10,0L0,5')
        .attr('fill', '#000')

  removeNode: (id) ->
    i = 0
    n = @findNode(id)
    while i < @links.length
      if @links[i]['source'] is n or @links[i]['target'] is n
        @links.splice i, 1
      else
        i++
    @nodes.splice(@findNodeIndex(id), 1)
    @update()

  removeLink: (source, target) ->
    i = 0
    while i < @links.length
      if @links[i].source.id is source and @links[i].target.id is target
        @links.splice i, 1
        break
      i++
    @update()

  removeallLinks: ->
    @links.splice 0, @links.length
    @update()

  removeAllNodes: ->
    @nodes.splice 0, @links.length
    @update()

  addLink: (source, target, value) ->
    @links.push
      'source': @findNode(source)
      'target': @findNode(target)
      'value': value

  findNode: (id) ->
    for i of @nodes
      if @nodes[i]['id'] is id
        return @nodes[i]
    return

  findNodeIndex: (id) ->
    i = 0
    while i < @nodes.length
      if @nodes[i].id is id
        return i
      i++
    return

  update: ->
    link = @vis
      .selectAll 'polyline'
      .data @links, (d) -> "#{d.source.id}-#{d.target.id}"

    link
      .enter()
      .append('polyline')
        .style('marker-mid', 'url(#start-arrow)')
        .attr 'id', (d) -> "#{d.source.id}-#{d.target.id}"
        .attr 'stroke-width', (d) -> d.value / 10
        .attr 'stroke', '#000'

    link
      .append 'title'
      .text (d) -> d.value

    link.exit().remove()

    node = @vis
      .selectAll 'g.node'
      .data @nodes, (d) -> d.id

    nodeEnter = node
      .enter()
      .append 'g'
        .attr 'class', 'node'
      .call @drag

    nodeEnter
      .append 'svg:circle'
        .attr 'r', 12
        .attr 'id', (d) -> "Node;#{d.id}"
        .attr 'class', 'nodeStrokeClass'
        .attr 'fill', (d) => @color(d.id)

    nodeEnter
      .append 'svg:text'
        .attr 'class', 'textClass'
        .attr 'x', 14
        .attr 'y', '.31em'
        .text (d) -> d.id

    node.exit().remove()

    @force.on 'tick', ->
      node.attr 'transform', (d) -> "translate(#{d.x}, #{d.y})"

      #: Use below when the links are "lines"
      # link
      #   .attr 'x1', (d) -> d.source.x
      #   .attr 'y1', (d) -> d.source.y
      #   .attr 'x2', (d) -> d.target.x
      #   .attr 'y2', (d) -> d.target.y

      link.attr 'points', (d) ->
        sx = d.source.x
        sy = d.source.y
        tx = d.target.x
        ty = d.target.y
        "#{sx},#{sy} #{(sx + tx)/2},#{(sy + ty)/2} #{tx},#{ty}"

    # Restart the force layout.
    @force
      .gravity .01
      .charge -80000
      .friction 0
      .linkDistance (d) -> d.value * 10
      .size [@w, @h]
      .start()

  keepNodesOnTop: ->
    $('.nodeStrokeClass').each (index) ->
      gnode = @parentNode
      gnode.parentNode.appendChild gnode

module.exports = Graph: Graph
