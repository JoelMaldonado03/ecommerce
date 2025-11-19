const form = document.getElementById('productForm');
const message = document.getElementById('message');
const tableBody = document.getElementById('productTable');

// URL del backend (ajusta si es necesario)
const API_URL = 'http://localhost:8000/products';

// Enviar nuevo producto
form.addEventListener('submit', async (e) => {
  e.preventDefault();
  const formData = new FormData(form);
  const data = Object.fromEntries(formData.entries());

  try {
    const res = await fetch(API_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        name: data.name,
        description: data.description,
        price: Number(data.price)
      })
    });

    if (!res.ok) throw new Error('Error al subir producto');

    message.textContent = '✅ Producto agregado con éxito';
    message.className = 'text-green-400 text-center';
    form.reset();
    cargarProductos();
  } catch (err) {
    console.error(err);
    message.textContent = '❌ No se pudo agregar el producto';
    message.className = 'text-red-400 text-center';
  }
});

// Cargar productos existentes
async function cargarProductos() {
  try {
    const res = await fetch(API_URL);
    const productos = await res.json();
    tableBody.innerHTML = '';

    productos.forEach(p => {
      const row = document.createElement('tr');
      row.innerHTML = `
        <td class="py-2">${p.name}</td>
        <td class="py-2">${p.description}</td>
        <td class="py-2">$${p.price}</td>
      `;
      tableBody.appendChild(row);
    });
  } catch (err) {
    console.error('Error cargando productos', err);
  }
}

cargarProductos();
