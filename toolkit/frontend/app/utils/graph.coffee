class Graph
  constructor: (opts) ->
    {@w, @h, elem} = opts
    @color = d3.scale.category10()
    @initEvents()
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

  addNode: (n) ->
    @nodes.push n

  initEvents: ->
    self = @
    @zoom = d3.behavior.zoom()
      .scaleExtent [-10, 10]
      .on "zoom", =>
        @vis.attr "transform",
          "translate(#{d3.event.translate}) scale(#{d3.event.scale})"

    @drag = d3.behavior.drag()
      .origin (d) -> d
      .on "dragstart", (d) ->
        d3.select(@).classed "fixed", d.fixed = no
        self.resume()
        d3.event.sourceEvent.stopPropagation()

      .on "drag", (d) ->
        d3.select(@)
          .attr "cx", d.x = d3.event.x
          .attr "cy", d.y = d3.event.y
        self.resume()
        d3.event.sourceEvent.stopPropagation()

      .on "dragend", (d) ->
        d3.select(@).classed "fixed", d.fixed = yes
        d3.event.sourceEvent.stopPropagation()

    @click_def = (e, f) =>
      @node_click_handle(e, f)

    @dblclk = (d) ->
      d3.select(@).classed "fixed", d.fixed = no

  resume: ->
    unless @force.alpha() > 0 then @force.resume()

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

  addLink: (source, target, value, kind) ->
    @links.push
      source: @findNode(source)
      target: @findNode(target)
      value: value
      kind: kind

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
        .attr 'stroke', (d) -> if d.kind is 'host' then '#049372' else '#AAA'

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
        .on 'dblclick', @dblclk
        .on 'click', @click_def
      .call @drag

    nodeEnter
      .append 'svg:text'
        .attr 'class', 'textClass'
        .attr 'x', 0
        .attr 'y', 0
        .attr 'text-anchor', 'middle'
        .text (d) -> d.id

    nodeEnter
      .append 'svg:circle'
        .attr 'r', 10
        .attr 'x', 0
        .attr 'y', 0
        .attr 'id', (d) -> "Node;#{d.id}"
        .attr 'class', 'nodeStrokeClass'
        .attr 'fill', (d) -> d.color

    nodeLabelEnter = nodeEnter.append 'g'
        .attr 'class', 'nodelabel'

    nodeLabelEnter
        .append 'svg:rect'
          .attr 'rx', 2
          .attr 'ry', 2
          .attr 'x', (d) -> -(@parentNode.parentNode.getBBox().width + 10) / 2
          .attr 'y', -9
          .attr 'width', (d) -> @parentNode.parentNode.getBBox().width + 10
          .attr 'height', 18
          .attr 'id', (d) -> "Rect;#{d.id}"
          .attr 'class', 'nodeStrokeClass'
          .attr 'fill', (d) -> d.color

    nodeLabelEnter
        .append 'svg:text'
          .attr 'class', 'label-main'
          .attr 'x', 0
          .attr 'y', 4
          .attr 'text-anchor', 'middle'
          .text (d) -> d.id

    nodeEnter.attr 'x', (d) -> -@.getBBox().width/2

    node.exit().remove()

    @force.on 'tick', ->
      node.attr 'transform', (d) -> "translate(#{d.x}, #{d.y})"

      link.attr 'points', (d) ->
        #: Correct the magic paddings that were added manually, above.
        sx = d.source.x #- 5
        sy = d.source.y #- 13
        tx = d.target.x #- 5
        ty = d.target.y #- 13

        #: Find The Width and height
        # sw = d3.select("rect[id='Node;#{d.source.id}']").attr("width")
        # sh = d3.select("rect[id='Node;#{d.source.id}']").attr("height")

        # tw = d3.select("rect[id='Node;#{d.target.id}']").attr("width")
        # th = d3.select("rect[id='Node;#{d.target.id}']").attr("height")

        # p_s = [
        #   [sx + (sw / 2), (sy / 1)]
        #   [sx + (sw / 1), sy + (sh / 2)]
        #   [sx + (sw / 2), sy + (sh / 1)]
        #   [(sx / 1),      sy + (sh / 2)]
        # ]

        # p_t = [
        #   [tx + (tw / 2), (ty / 1)]
        #   [tx + (tw / 1), ty + (th / 2)]
        #   [tx + (tw / 2), ty + (th / 1)]
        #   [(tx / 1),      ty + (th / 2)]
        # ]

        # pairs = [
        #   [p_s[0], p_t[1]]
        #   [p_s[0], p_t[2]]
        #   [p_s[0], p_t[3]]
        #   [p_s[1], p_t[0]]
        #   [p_s[1], p_t[2]]
        #   [p_s[1], p_t[3]]
        #   [p_s[2], p_t[1]]
        #   [p_s[2], p_t[0]]
        #   [p_s[2], p_t[3]]
        #   [p_s[3], p_t[1]]
        #   [p_s[3], p_t[2]]
        #   [p_s[3], p_t[0]]
        # ]

        # #: Find shortest edge.
        # cp = _.minBy pairs, (d) ->
        #   ((d[0][0] - d[1][0])**2 + (d[0][1] - d[1][1])**2)

        # sx = sx + (sw / 2)
        # sy = sy + (sh / 2)
        # tx = tx + (tw / 2)
        # ty = ty + (th / 2)

        # sx = cp[0][0]
        # sy = cp[0][1]
        # tx = cp[1][0]
        # ty = cp[1][1]

        #: Make the node coordinates for source.

        "#{sx},#{sy} #{(sx + tx)/2},#{(sy + ty)/2} #{tx},#{ty}"

    # Restart the force layout.
    @force
      .gravity .05
      .charge -1200
      .friction 0.3
      .linkDistance (d) -> d.value * 10
      .size [@w, @h]
      .start()

    @keepNodesOnTop()

  keepNodesOnTop: ->
    $('.nodeStrokeClass').each (index) ->
      gnode = @parentNode
      gnode.parentNode.appendChild gnode

module.exports = Graph: Graph
