
rivets = require('rivets').rvt
_ = require('lodash')

class GraphView
  constructor: (opts)->
    {@width, @height, @elem} = opts

    @nodemousedn = no
    @color = d3.scale.category20()
    @webcola = cola.d3adaptor().size [@width, @height]

    @init_containers()

  init_containers: ->
    @outer = d3.select(@elem)
      .append 'svg'
      .attr   'width', @width
      .attr   'height', @height
      .attr   'pointer-events', 'all'

    @outer.append('rect')
      .attr 'class', 'background'
      .attr 'width', '100%'
      .attr 'height', '100%'
      .call d3.behavior.zoom().on 'zoom', @redraw

    @vis = @outer.append('g')

  redraw: =>
    return if @nodemousedn
    velocity = 10
    scale = d3.event.scale ** velocity
    translateY = (300 - (300 * scale)) / 2
    translateX = (200 - (200 * scale)) / 2

    @vis.attr 'transform',
      "translate(#{translateX}, #{translateY}) scale(#{scale})"

  routine: ->
    d3.json '/static/mis.json', (error, graph) =>
      @webcola.nodes(graph.nodes)
        .links(graph.links)
        .jaccardLinkLengths(40, 0.7)
        .start 30

      link = @vis.selectAll('.link')
        .data(graph.links).enter()
        .append 'line'
        .attr 'class', 'link'
        .style 'stroke-width', (d) -> Math.sqrt d.value

      node = @vis.selectAll('.node')
        .data(graph.nodes).enter()
        .append 'circle'
        .attr 'class', 'node'
        .attr 'r', 5
        .style 'fill', (d) => @color d.group
        .call @webcola.drag

      node.append('title').text (d) -> d.name

      @webcola.on 'tick', ->
        link.attr 'x1', (d) -> d.source.x
            .attr 'y1', (d) -> d.source.y
            .attr 'x2', (d) -> d.target.x
            .attr 'y2', (d) -> d.target.y

        node.attr 'cx', (d) -> d.x
            .attr 'cy', (d) -> d.y

class UserView
  constructor: (opts) ->
    @select_init()
    @bound_select_input = {}
    @select_init()

  rivets_init: ->
    @rivets_view = rivets.bind($('#nodes'), {nodes: @bound_select_input})
    @bound_select_input.genes = ['RIN2']

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
