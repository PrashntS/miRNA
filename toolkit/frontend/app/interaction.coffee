
rivets = require('rivets').rvt
_ = require('lodash')

class GraphView
  constructor: (opts)->
    {@width, @height, @elem} = opts

    @nodemousedn = no
    @fill = d3.scale.category20()
    @webcola = cola.d3adaptor().size [@width, @height]

    @force = d3.layout.force()
      .gravity(.05)
      .charge(-240)
      .linkDistance(50)
      .size([@width, @height])

    @init_containers()

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

  redraw: =>
    @vis.attr 'transform',
      "translate(#{d3.event.translate}) scale(#{d3.event.scale})"

  graph_factory: (dat) =>
    $.getJSON "/api/graph?#{dat}"
    .done (dat) =>
      {target_list, host_list, miRNA_store, genes_store} = dat

  routine: ->
    d3.json '/api/graph?genes=RIN2&mirna=', (error, graph) =>

      radius = 10
      width =

      link = @svg
        .selectAll('line')
        .data(graph.links)
        .enter()
        .append('line')

      node = @svg
        .selectAll('circle')
        .data(graph.nodes)
        .enter()
        .append('circle')
        .attr('r', radius - .75)
        .style('fill', (d) => @fill d.group)
        .style('stroke', (d) => d3.rgb(@fill(d.group)).darker())
        .call(@force.drag)

      tick = =>
        node.attr('cx', (d) =>
          d.x = Math.max(radius, Math.min(@width - radius, d.x)))
        .attr 'cy', (d) =>
          d.y = Math.max(radius, Math.min(@height - radius, d.y))

        link.attr 'x1', (d) -> d.source.x
            .attr 'y1', (d) -> d.source.y
            .attr 'x2', (d) -> d.target.x
            .attr 'y2', (d) -> d.target.y
        return

      @force
        .nodes(graph.nodes)
        .links(graph.links)
        .on('tick', tick)
        .start()

class UserView
  constructor: (opts) ->
    @select_init()
    @bound_select_input = {}
    @select_init()
    @rivets_init()

  rivets_init: ->
    @rivets_view = rivets.bind($('#nodes'), {nodes: @bound_select_input})
    @bound_select_input.genes = ['RIN2']

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

    g.routine()
    # g.graph_factory ui.select_val()


  init: ->
    class Fanck
      constructor: ->
        @message = ''
        @speed = 0
        @col = '#FFFFFF'
        @explode = () ->
          console.log "Hey"

    if $('.cd-stretchy-nav').length > 0
      stretchyNavs = $('.cd-stretchy-nav')
      stretchyNavs.each ->
        stretchyNav = $(this)
        stretchyNavTrigger = stretchyNav.find('.cd-nav-trigger')
        stretchyNavTrigger.on 'click', (event) ->
          event.preventDefault()
          stretchyNav.toggleClass 'nav-is-visible'
          return
        return
      $(document).on 'click', (event) ->
        !$(event.target).is('.cd-nav-trigger') and !$(event.target).is('.cd-nav-trigger span') and stretchyNavs.removeClass('nav-is-visible')
        return

    func = new Fanck

    gui = new dat.GUI
      autoPlace: false
    f1 = gui.addFolder 'conc'
    f2 = gui.addFolder 'colors'
    f1.add func, 'message'
    f1.add func, 'speed', -5, 5
    f2.add func, 'explode'
    f2.addColor func, 'col'

    @G = new jsnx.DiGraph

    jsnx.draw @G,
      element: '#graphcanvas'
      withLabels: true
      # labels: -> 'LOL!?'
      edgeLabels: -> 'xD'
      nodeStyle:
        fill: (d) ->
          d.data.color
      labelStyle: fill: 'black'
      # edgeStyle:
      #   fill: '#6C7A89'
      #   opacity: 0.5
      stickyDrag: true
      weighted: yes
      weightedStroke: yes
      weights: (s) ->
        console.log _.random(10), s
        _.random(10)
    , true

    a = 2
    graph_factory = (opts) =>
      $.getJSON "/api/graph?#{$.param(@nodes, true)}"
      .done (dat) =>
        $(".overlay-info").fadeOut()
        $(".overlay-terra").fadeOut()
        {target_list, host_list, miRNA_store, genes_store} = dat

        @G.addNodesFrom miRNA_store,
          color: '#FF0000'
          strokeWidth: 0

        @G.addNodesFrom genes_store,
          color: '#87D37C'
          strokeWidth: 0

        @G.addEdgesFrom target_list
        @G.addEdgesFrom host_list

    $('#data_gui').html(gui.domElement)

    $('select.rivets').on 'change', =>
      graph_factory()

    graph_factory()

  node_val: ->
    @nodes
