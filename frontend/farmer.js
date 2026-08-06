const productForm=document.getElementById("productForm");

const productTable=document.getElementById("productTable");

let products=[];

function loadProducts(){

productTable.innerHTML="";

products.forEach((product,index)=>{

productTable.innerHTML+=`

<tr>

<td>${product.name}</td>

<td>${product.quantity} Kg</td>

<td>₹${product.price}</td>

<td>${product.harvestDate}</td>

<td>

<button class="edit-btn" onclick="editProduct(${index})">
Edit
</button>

<button class="delete-btn" onclick="deleteProduct(${index})">
Delete
</button>

</td>

</tr>

`;

});

}

productForm.addEventListener("submit",function(e){

e.preventDefault();

const product={

name:document.getElementById("productName").value,

quantity:document.getElementById("quantity").value,

price:document.getElementById("price").value,

harvestDate:document.getElementById("harvestDate").value,

description:document.getElementById("description").value

};

products.push(product);

loadProducts();

productForm.reset();

alert("Product Added Successfully.");

});

function deleteProduct(index){

if(confirm("Delete this product?")){

products.splice(index,1);

loadProducts();

}

}

function editProduct(index){

const product=products[index];

document.getElementById("productName").value=product.name;

document.getElementById("quantity").value=product.quantity;

document.getElementById("price").value=product.price;

document.getElementById("harvestDate").value=product.harvestDate;

document.getElementById("description").value=product.description;

products.splice(index,1);

loadProducts();

}

loadProducts();