$(function(){
        $('#btnSignUp').click(function(){
                var btn = $(this);

                btn.prop('disabled',true);

                $.ajax({
                        url: '/',
                        data: $('form').serialize(),
                        type: 'POST',
                        success: function(response){
                        console.log(response);

                        var json = JSON.parse(response);
                        var _ret = json['ret'];
                        var _msg = json['msg'];

                        console.log('response');
                        console.log(_ret);
                        console.log(_msg);
                        
                        if (_ret === 'True'){
                                                
                        var formatted_results = ""
                        for (i=0;i<json['closestWord'].length;i++) {
                            splice = json['closestWord'][i][0].split("/")
                            stub = splice[splice.length-1]
                            formatted_results += "<h3><a href='"+json['closestWord'][i][0]+"' target='_blank'>"+stub+"</a> ("+json['closestWord'][i][1]+")</h3>"
                        }
                        console.log(formatted_results);
                        
                        $("#closestSpot").html("<h3>Closest Scripts" + formatted_results + "</h3>");
                                btn.prop('disabled',false);

                        } else {
                        
                        $("#closestSpot").html("<h3>"+_msg+"</h3>");
                                console.log('error');
                                btn.prop('disabled',false);
                        }
                        },
                        error: function(error){
                                console.log(error);
                                btn.prop('disabled',false);
                        }
                });

        });
});
