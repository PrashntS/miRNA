
rivets.formatters.select2 = (value, selector) ->
  $(selector).val(value).trigger('change')
  console.log($(selector))
  return value

rivets.configure
  prefix: 'rv'
  preloadData: true
  rootInterface: '.'
  templateDelimiters: [
    '{'
    '}'
  ]

  adapter:
    observe: (obj, keypath, callback) ->
      obj.on 'change:' + keypath, callback
      return
    unobserve: (obj, keypath, callback) ->
      obj.off 'change:' + keypath, callback
      return
    get: (obj, keypath) ->
      obj.get keypath
    set: (obj, keypath, value) ->
      obj.set keypath, value
      return

  # handler: (target, event, binding) ->
  #   @call target, event, binding.view.models
  #   return

exports.rvt = rivets
