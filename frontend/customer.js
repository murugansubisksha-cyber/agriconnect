const productList=document.getElementById("productList");

const orderModal=document.getElementById("orderModal");

const orderForm=document.getElementById("orderForm");

const products=[

{
id:1,
name:"Organic Tomato",
price:40,
farmer:"Ramesh",
stock:120
},

{
id:2,
name:"Fresh Onion",
price:28,
farmer:"Suresh",
stock:200
},

{
id:3,
name:"Potato",
price:35,
farmer:"Kumar",
stock:180
},

{
id:4,
name:"Carrot",
price:55,
farmer:"Arun",
stock:90
},

{
id:5,
name:"Groundnut",
price:95,
farmer:"Mohan",
stock:75
},

{
id:6,
name:"Banana",
price:30,
farmer:"Saravanan",
stock:300
}

];

function loadProducts(){

productList.innerHTML="";

products.forEach(product=>{

productList.innerHTML+=`

<div class="product-card">

<h3>${product.name}</h3>

<p><strong>Farmer:</strong> ${product.farmer}</p>

<p><strong>Price:</strong> ₹${product.price}/Kg</p>

<p><strong>Available:</strong> ${product.stock} Kg</p>

<button onclick="openModal(${product.id})">
Request Quotation
</button>

</div>

`;

});

}

function openModal(id){

const product=products.find(p=>p.id===id);

document.getElementById("productId").value=product.id;

document.getElementById("productName").value=product.name;

document.getElementById("quantity").value="";

document.getElementById("offeredPrice").value="";

orderModal.style.display="flex";

}

function closeModal(){

orderModal.style.display="none";

}

window.onclick=function(event){

if(event.target===orderModal){

closeModal();

}

}

orderForm.addEventListener("submit",function(e){

e.preventDefault();

const quantity=document.getElementById("quantity").value;

const offeredPrice=document.getElementById("offeredPrice").value;

if(quantity===""||offeredPrice===""){

alert("Please fill all fields.");

return;

}

alert("Quotation sent successfully!");

closeModal();

});

loadProducts();