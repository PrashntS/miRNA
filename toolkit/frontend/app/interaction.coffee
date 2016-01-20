
rivets = require('rivets').rvt
_ = require('lodash')

class Graph
  constructor: (opts)->
    @G = new jsnx.DiGraph
    @r = {}

  fetch: (dat, func) ->
    $.getJSON "/api/graph?#{dat}"
    .done (dat) =>
      {target_list, host_list, miRNA_store, genes_store} = dat

      @miRNAs = _.union @miRNAs, miRNA_store

      @G.addNodesFrom miRNA_store
      @G.addNodesFrom genes_store
      @G.addEdgesFrom target_list
      @G.addEdgesFrom host_list

      @r = jsnx.toDictOfLists(@G)

      if func then func()

  nodes: () ->
    ret = []

    for k, v of @r
      ret.push
        name: k
        type: if _.indexOf(@miRNAs, k) > -1 then 'miRNA' else 'Gene'
        weight: v.length

    ret

  edges: () ->
    n = @nodes()
    ret = []
    for src, v of @r
      for target in v
        ret.push
          source: _.findIndex n, (d) -> d.name is src
          target: _.findIndex n, (d) -> d.name is target

    ret

class GraphView
  constructor: (opts)->
    {@width, @height, @elem} = opts
    @nodes = []
    @links = []
    @miRNAs = []

    @G = new Graph

    @nodemousedn = no
    @fill = d3.scale.category20()

    @forcem = d3.layout.force()
      .gravity(.5)
      .charge(-240)
      .linkDistance(100)
      .size([@width, @height])

    @force = cola.d3adaptor()
      .linkDistance(200)
      # .flowLayout("y", 30)
      # .avoidOverlaps(true)

      # .symmetricDiffLinkLengths(60)

      .size([@width, @height])

    @init_containers()
    @init_defs()

  init_containers: ->
    @svg = d3.select(@elem)
      .append 'svg'
      .attr   'class', 'svgpos'
      .attr   'width', @width
      .attr   'height', @height
      .call(d3.behavior.zoom().on 'zoom', @redraw)

    @svg.append('rect')
      .attr('class', 'background')
      .attr('width', "100%")
      .attr('height', "100%")

    @vis = @svg.append('g')

  init_defs: ->
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
        .attr('refX', 0)
        .attr('markerWidth', 5)
        .attr('markerHeight', 5)
        .attr('orient', 'auto')
      .append('svg:path')
        .attr('d', 'M0,-5L10,0L0,5')
        .attr('fill', '#000')

  redraw: =>
    console.log d3.event
    @vis.attr 'transform',
      "translate(#{d3.event.translate}) scale(#{d3.event.scale})"

  get_graph: (dat) ->

    @G.fetch dat, =>
      @nodes = @G.nodes()
      @links = @G.edges()

      @routine()

  graph_factory: (dat) ->
    # $.getJSON "/api/graph?#{dat}"
    # .done (dat) =>
    d3.json "/api/graph?#{dat}", (error, graph) =>
      {nodes, links} = graph

      new jsnx.DiGraph

      @nodes = _.unionWith @nodes, nodes, (x, y) ->
        x.name is y.name

      @links = _.unionWith @links, links, (x, y) ->
        if typeof y.source is 'number' and typeof x.source is 'number'
          nodes[x.source].name is nodes[y.source].name and
          nodes[x.target].name is nodes[y.target].name

        else if typeof y.source is 'object' and typeof x.source is 'number'
          nodes[x.source].name is y.source.name and
          nodes[x.target].name is y.target.name

        else if typeof y.source is 'object' and typeof x.source is 'object'
          x.source.name is y.source.name and
          x.target.name is y.target.name

        else if typeof y.source is 'number' and typeof x.source is 'object'
          x.source.name is nodes[y.source].name and
          x.target.name is nodes[y.target].name

      @routine()

  routine: ->
    radius = 5

    link = @vis
      .selectAll('.link')
      .data(@links)
      .enter()
      .append('polyline')
      .style('marker-mid', 'url(#start-arrow)')
      .attr('class', 'link')

    node = @vis
      .selectAll('.node')
      .data(@nodes)
      .enter()
      .append('g')
      .attr("class", "node")
      .call(@force.drag)

    circle = node
      .append('circle')
      .attr('r', (d) -> radius)
      .style('fill', (d) => @fill d.type)
      # .style('stroke', (d) => d3.rgb(@fill(d.group)).darker())
      .on 'mouseover', ->
        d3.select(@)
          .transition()
          .duration(200)
          .attr("r", 16)
      .on 'mouseout', ->
        d3.select(@)
          .transition()
          .duration(200)
          .attr("r", 5)

    label = node.append("text")
      .attr("dy", ".35em")
      .text((d) -> d.name)

    tick = ->
      circle.attr 'cx', (d) -> d.x
          .attr 'cy', (d) -> d.y

      link.attr 'points', (d) ->
        sx = d.source.x
        sy = d.source.y
        tx = d.target.x
        ty = d.target.y
        "#{sx},#{sy} #{(sx + tx)/2},#{(sy + ty)/2} #{tx},#{ty}"

      label
        .attr "x", (d) -> d.x + 8
        .attr "y", (d) -> d.y

    @force
      .nodes(@nodes)
      .links(@links)
      .jaccardLinkLengths(100,0.7)
      .on('tick', tick)
      .start()


class UserView
  constructor: (opts) ->
    @select_init()
    @bound_select_input = {}
    @select_init()
    @rivets_init()
    @toolbar_init()

  rivets_init: ->
    @rivets_view = rivets.bind($('#nodes'), {nodes: @bound_select_input})
    @bound_select_input.genes = ['RIN2']

  toolbar_init: ->
    @toolbar = $('.cd-stretchy-nav')
    @toolbar.find('.cd-nav-trigger').on 'click', =>
      @toolbar.toggleClass 'nav-is-visible'

  select_val: ->
    $.param(@bound_select_input, true)

  select_init: ->
    factory_select = (opts) ->
      ajax:
        url: opts.uri,
        dataType: 'json',
        delay: 250,
        data: (param) ->
          return {
            q__icontains: param.term
            _skip: (param.page - 1) * 20 if param.page and param.page > 0
            _limit: 20
          }
        processResults: (data, params) ->
          params.page = params.page || 1

          return {
            results: _.map data.data, (dat) ->
              dat.id = dat.symbol
              dat.text = dat.symbol
              dat
            pagination:
              more: data.has_more
          }
        cache: true
      escapeMarkup: (markup) -> markup
      placeholder: opts.placeholder
      minimumInputLength: 2
      maximumSelectionLength: 5
      templateResult: opts.templateResult
      templateSelection: (obj) -> obj.symbol or obj.text

    $('.gene_select').select2 factory_select
      uri: '/api/gene'
      value: 'CDKN1A'
      placeholder: "Please Enter a Few Genes"
      templateResult: (obj) ->
        return obj.text if obj.loading
        markup = """
          <div class="dropdown-card">
            <h1>#{obj.symbol}</h1>
            <p>#{obj.description}</p>
            <ul>
              <li>
                <strong>Targeted By</strong>: #{obj.targeted_by.length} miRNAs
              </li>
              <li>
                <strong>Host of (miRNA)</strong>:
                  #{obj.host_of?.symbol || 'N.A.'}
              </li>
              <li>
                <strong>ESID</strong>: #{obj.names[0]}
              </li>
            </ul>
          </div>
        """
        markup

    $('.mirna_select').select2 factory_select
      uri: '/api/mirna'
      placeholder: "Please Enter a Few miRNA"
      templateResult: (obj) ->
        return obj.text if obj.loading
        markup = """
          <div class="dropdown-card">
            <h1>#{obj.symbol}</h1>
            <ul>
              <li>
                <strong>Targets</strong>: #{obj.targets.length} Genes
              </li>
              <li>
                <strong>Host Gene</strong>: #{obj.host?.symbol || 'N.A.'}
              </li>
              <li>
                <strong><a href="#{obj.mirbase_url}">miRBase Link</a></strong>
              </li>
            </ul>
          </div>
        """
        markup

exports.interaction =
  mmn: ->
    width = $(".overlay-terra").width()
    height = $(".overlay-terra").height()

    ui = new UserView

    g = new GraphView
      width: width
      height: height
      elem: '#graphcanvas'

    g.get_graph ui.select_val()

    # g.routine()
    # $('select.rivets').on 'change', ->
    #   g.get_graph ui.select_val()

    # g2 = new jsnx.DiGraph

    # $.getJSON "/api/graph?genes=CDKN1A"
    # .done (dat) ->
    #   {target_list, host_list, miRNA_store, genes_store} = dat

    #   g2.addNodesFrom miRNA_store
    #   g2.addNodesFrom genes_store
    #   g2.addEdgesFrom target_list
    #   g2.addEdgesFrom host_list

    #   console.log g2.edges()

  init: ->
    class Fanck
      constructor: ->
        @message = ''
        @speed = 0
        @col = '#FFFFFF'
        @explode = () ->
          console.log "Hey"

    func = new Fanck

    gui = new dat.GUI
      autoPlace: false
    f1 = gui.addFolder 'conc'
    f2 = gui.addFolder 'colors'
    f1.add func, 'message'
    f1.add func, 'speed', -5, 5
    f2.add func, 'explode'
    f2.addColor func, 'col'


    $('#data_gui').html(gui.domElement)

    $('select.rivets').on 'change', =>
      graph_factory()

    graph_factory()

  node_val: ->
    @nodes
