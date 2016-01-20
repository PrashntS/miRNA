class Graph
  constructor: (opts) ->
    # set up the D3 visualisation in the specified element
    {@w, @h, elem} = opts
    console.log opts
    @color = d3.scale.category10()
    @vis = d3.select elem
      .append 'svg:svg'
        .attr 'width', @w
        .attr 'height', @h
        .attr 'id', 'svg'
        .attr 'pointer-events', 'all'
        .attr 'viewBox', "0 0 #{@w} #{@h}"
        .attr 'perserveAspectRatio', 'xMinYMid'
      .append 'svg:g'

    @force = d3.layout.force()
    @nodes = @force.nodes()
    @links = @force.links()

  addNode: (id) ->
    @nodes.push 'id': id
    @update()

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
    @update()

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
      .selectAll 'line'
      .data @links, (d) -> "#{d.source.id}-#{d.target.id}"

    link
      .enter()
      .append 'line'
        .attr 'id', (d) -> "#{d.source.id}-#{d.target.id}"
        .attr 'stroke-width', (d) -> d.value / 10
        .attr 'class', 'link'

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
      .call @force.drag

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

      link
        .attr 'x1', (d) -> d.source.x
        .attr 'y1', (d) -> d.source.y
        .attr 'x2', (d) -> d.target.x
        .attr 'y2', (d) -> d.target.y

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

drawGraph = ->
  graph = new myGraph('#svgdiv')

  graph.addNode 'Sophia'
  graph.addNode 'Daniel'
  graph.addNode 'Ryan'
  graph.addNode 'Lila'
  graph.addNode 'Suzie'
  graph.addNode 'Riley'
  graph.addNode 'Grace'
  graph.addNode 'Dylan'
  graph.addNode 'Mason'
  graph.addNode 'Emma'
  graph.addNode 'Alex'
  graph.addLink 'Alex', 'Ryan', '20'
  graph.addLink 'Sophia', 'Ryan', '20'
  graph.addLink 'Daniel', 'Ryan', '20'
  graph.addLink 'Ryan', 'Lila', '30'
  graph.addLink 'Lila', 'Suzie', '20'
  graph.addLink 'Suzie', 'Riley', '10'
  graph.addLink 'Suzie', 'Grace', '30'
  graph.addLink 'Grace', 'Dylan', '10'
  graph.addLink 'Dylan', 'Mason', '20'
  graph.addLink 'Dylan', 'Emma', '20'
  graph.addLink 'Emma', 'Mason', '10'

  # callback for the changes in the network
  setTimeout (->
    graph.addLink 'Alex', 'Sophia', '20'
    graph.keepNodesOnTop()
  ), 2000
  setTimeout (->
    graph.addLink 'Sophia', 'Daniel', '20'
    graph.keepNodesOnTop()
  ), 4000
  setTimeout (->
    graph.addLink 'Daniel', 'Alex', '20'
    graph.keepNodesOnTop()
  ), 5000

  setTimeout (->
    graph.removeLink 'Dylan', 'Mason'
    graph.addLink 'Dylan', 'Mason', '8'
    graph.keepNodesOnTop()
  ), 8000


