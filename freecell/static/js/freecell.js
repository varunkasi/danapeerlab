CURRENT_ID = 0;
function getParameterByName(name) {

    var match = RegExp('[?&]' + name + '=([^&]*)')
                    .exec(window.location.search);

    return match && decodeURIComponent(match[1].replace(/\+/g, ' '));

}

function set_report_value(report_id, widget_id, key, value) {
  var html = $.ajax({
    url: "set_value",
    data: {report:report_id, widget:widget_id, key:key, value:value },
    async: false
  }).responseText;
};

function set_value(widget_id, key, value) {
  return set_report_value(
      getParameterByName("id"), 
      widget_id,
      key, value);
};

SAVERS = {};
VALIDATORS = {}

function register_validate(saver_id, validate_func) {
  if (!(saver_id in VALIDATORS)) {
    VALIDATORS[saver_id] = [];
  }
  VALIDATORS[saver_id].push(validate_func);
};

function register_save(saver_id, save_func) {
  if (!(saver_id in SAVERS)) {
    SAVERS[saver_id] = [];
  }
  SAVERS[saver_id].push(save_func);
};

function validate(saver_id) {
    if (!(saver_id in VALIDATORS)) {
    return true;
  }
  functions = VALIDATORS[saver_id];
  ret = true;
  for (var i=0; i<functions.length; i++) {
    ret = ret && functions[i]();
  }
  return ret;
};

function save(saver_id) {
  if (!(saver_id in SAVERS)) {
    return;
  }
  functions = SAVERS[saver_id];
  for (var i=0; i<functions.length; i++) {
    functions[i]();
  }
};
