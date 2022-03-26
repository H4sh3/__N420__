


// get content of flask templat
  $(function() {
    $('a#calculate').bind('click', function() {
      $.getJSON($SCRIPT_ROOT + 'preferences/_options', {
        a: $('input[name="a"]').val(),
        b: $('input[name="b"]').val(),
        c: $('input[name="c"]').val()
      }, function(data) {
        $("#result").text(data.result);
        $("#pointsd").val(data.result);
      });
      return false;
    });
  });

