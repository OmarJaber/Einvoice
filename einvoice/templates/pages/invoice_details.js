
frappe.ready(function () {

    var invoice = getUrlParameter('invoice');
    var is_return = getUrlParameter('is_return');
    var amount_without_tax = getUrlParameter('amount_without_tax');
    var tax_amount = getUrlParameter('tax_amount');
    var total_amount = getUrlParameter('total_amount');


    $(".invoice").text(invoice);
    $(".amount_without_tax").text(amount_without_tax);
    $(".tax_amount").text(tax_amount);
    $(".total_amount").text(total_amount);
    


    frappe.call({
        method: 'einvoice.templates.pages.invoice_details.get_invoice_details',
        args:{'invoice': invoice},
        callback: function(r) {
          if(r.message){
            
            $(".company").html(r.message[0]);
            $(".tax_id").html(r.message[1]);

            if(is_return==1){
                $(".returned_invoice").text("فاتورة مرتجع");

                date = "<tr><th>التاريخ</th><td>"+r.message[2]+"</td></tr>"
                time = "<tr><th>الوقت</th><td>"+r.message[3]+"</td></tr>"

                $(".invoice_table tr:nth-child(2)").after(date);
                $(".invoice_table tr:nth-child(3)").after(time);

            }else{

                date = "<tr><th>التاريخ</th><td>"+r.message[2]+"</td></tr>"
                time = "<tr><th>الوقت</th><td>"+r.message[3]+"</td></tr>"

                $(".invoice_table tr:first-child").after(date);
                $(".invoice_table tr:nth-child(2)").after(time);


            }


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


