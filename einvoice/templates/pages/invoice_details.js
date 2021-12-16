
frappe.ready(function () {

    var invoice = getUrlParameter('invoice');

    $(".invoice").text(invoice);    


    frappe.call({
        method: 'einvoice.templates.pages.invoice_details.get_invoice_details',
        args:{'invoice': invoice},
        callback: function(r) {
          if(r.message){
            
            $(".company").html(r.message[0]);
            $(".tax_id").html(r.message[1]);


            

            date = "<tr><th>التاريخ</th><td>"+r.message[2]+"</td></tr>"
            time = "<tr><th>الوقت</th><td>"+r.message[3]+"</td></tr>"

            $(".invoice_table tr:first-child").after(date);
            $(".invoice_table tr:nth-child(2)").after(time);


            $(".amount_without_tax").text(r.message[4]);
            $(".tax_amount").text(r.message[5]);
            $(".total_amount").text(r.message[6]);




          }
        }
    });



    



});


function getUrlParameter(name) {
    name = name.replace(/[\[]/, '\\[').replace(/[\]]/, '\\]');
    var regex = new RegExp('[\\?&]' + name + '=([^&#]*)');
    var results = regex.exec(location.search);
    return results === null ? '' : decodeURIComponent(results[1].replace(/\+/g, ' '));
};


