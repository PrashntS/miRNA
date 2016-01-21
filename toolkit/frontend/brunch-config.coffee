module.exports = config:
  paths:
    public: '../miRNA/static'
  files:
    javascripts: joinTo:
      'js/libraries.js': (path) ->
        /^(bower_components)|(lodash)\//.test path
      'js/app.js': (path) ->
        /^(app)\//.test path
    stylesheets:
      joinTo:
        'css/libraries.css': /^bower_components\//
        'css/app.css': /^(app)/
      order:
        before: ['bower_components/normalize-css/normalize.css']
    templates: joinTo: 'js/app.js'
  plugins:
    coffeescript:
      bare: yes
    sass:
      mode: 'ruby'
      allowCache: true
      options:
        includePaths: (->
          bourbon = require('node-bourbon').includePaths
          neat = require('node-neat').includePaths
          bourbon.concat neat
        )()
    autoReload:
      enabled: yes
  npm:
    enabled: yes
    whitelist: ['lodash']

