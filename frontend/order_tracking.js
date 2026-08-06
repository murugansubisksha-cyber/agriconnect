const API_URL = "http://127.0.0.1:5000/api/orders";

document.addEventListener("DOMContentLoaded", loadOrders);

async function loadOrders(){

    const token = localStorage.getItem("access_token");

    const table = document.getElementById("orderTable");

    table.innerHTML = `
        <tr>
            <td colspan="7">Loading orders...</td>
        </tr>
    `;

    try{

        const response = await fetch(API_URL,{
            method:"GET",
            headers:{
                "Authorization":"Bearer "+token
            }
        });

        if(!response.ok){
            throw new Error("Unable to load orders");
        }

        const orders = await response.json();

        table.innerHTML="";

        if(orders.length===0){

            table.innerHTML=`
                <tr>
                    <td colspan="7">No orders found.</td>
                </tr>
            `;

            return;
        }

        orders.forEach(order=>{

            table.innerHTML += `
            <tr>

                <td>${order.id}</td>

                <td>${order.product_name}</td>

                <td>${order.quantity}</td>

                <td>₹${order.total_price}</td>

                <td>${order.payment_status}</td>

                <td>${order.order_status}</td>

                <td>

                    <button
                    class="track-btn"
                    onclick="showTracking('${order.order_status}')">

                    Track

                    </button>

                </td>

            </tr>
            `;

        });

    }

    catch(error){

        table.innerHTML=`
            <tr>
                <td colspan="7">
                    Failed to load orders.
                </td>
            </tr>
        `;

        console.error(error);

    }

}

function showTracking(status){

    document.getElementById("trackingModal").style.display="block";

    document.querySelectorAll(".step").forEach(step=>{
        step.classList.remove("active");
    });

    document.getElementById("step1").classList.add("active");

    const stages=[
        "Accepted",
        "Packed",
        "Out for Delivery",
        "Delivered"
    ];

    if(stages.includes(status))
        document.getElementById("step2").classList.add("active");

    if(["Packed","Out for Delivery","Delivered"].includes(status))
        document.getElementById("step3").classList.add("active");

    if(["Out for Delivery","Delivered"].includes(status))
        document.getElementById("step4").classList.add("active");

    if(status==="Delivered")
        document.getElementById("step5").classList.add("active");

}

function closeTracking(){

    document.getElementById("trackingModal").style.display="none";

}

window.onclick=function(event){

    const modal=document.getElementById("trackingModal");

    if(event.target===modal){

        closeTracking();

    }

};