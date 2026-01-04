const btnAdd = document.getElementById("addBook");
const btnBuscarISBN = document.getElementById("searchBtn");

btnAdd.addEventListener("click", () => {
  const añadidor = document.getElementById("añadidor");
  const form = document.getElementById("manualForm");
  const formEdit = document.getElementById("editarForm");


  if(form.style.display !== "block" && formEdit.style.display !== "block"){
    añadidor.style.display = "flex";
  }else{alert('Complete el cuadro manual.')}
});

btnBuscarISBN.addEventListener("click", () => {
  searchIsbn();
});

async function searchIsbn(){
  const codigo = document.getElementById("buscadorISBN") 
  const res = await fetch("/api/libro", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ isbn: codigo.value })
      });
  const resultado = await res.json();
  if (resultado['type'] == 'API'){
    alert(`Libro ${resultado['title']} agregado correctamente.`)
  }else if(resultado['type'] == 'manual'){
    mostrarFormularioManual(codigo.value);
  }else if(resultado['type'] == 'edit'){
    console.log(resultado)
    mostrarEdicionLibro(resultado['libro'])
  }
  cargarLibros()
  codigo.value = '';
  
}

function mostrarFormularioManual(isbn) {
  const form = document.getElementById("manualForm");
  form.style.display = "block";
  document.getElementById("isbn").value = isbn;

  form.onsubmit = async (e) => {
    e.preventDefault();
    const libro = {
      isbn: document.getElementById("isbn").value,
      titulo: document.getElementById("titulo").value,
      autor: document.getElementById("autor").value,
      editorial: document.getElementById("editorial").value,
      año: document.getElementById("anio").value,
      portada_url: document.getElementById("portada").value
    };

    const res = await fetch("/api/libro/manual", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(libro)
    })

    const resultado = await res.json();
    if (resultado['status'] == 200){
      alert(`Libro agregado manualmente: ${resultado['title']}`);
      form.reset();
      form.style.display = "none";
      cargarLibros()
    }else{alert(`Error al agregar el libro: ${resultado['title']}`);}
    
  };
}

function mostrarEdicionLibro(libro) {
  const formAgregar = document.getElementById("manualForm");
  formAgregar.style.display = "none";
  const form = document.getElementById("editarForm");
  form.style.display = "block";

  document.getElementById("edit-isbn").value = libro.isbn;
  document.getElementById("edit-titulo").value = libro.titulo;
  document.getElementById("edit-autor").value = libro.autor;
  document.getElementById("edit-editorial").value = libro.editorial;
  document.getElementById("edit-anio").value = libro.año;
  document.getElementById("edit-portada").value = libro.portada_url;
}

document.getElementById("btnGuardarEdicion").addEventListener("click", async () => {
  const form = document.getElementById("editarForm");
  
  const libroEditado = {
    isbn: document.getElementById("edit-isbn").value,
    titulo: document.getElementById("edit-titulo").value,
    autor: document.getElementById("edit-autor").value,
    editorial: document.getElementById("edit-editorial").value,
    año: document.getElementById("edit-anio").value,
    portada_url: document.getElementById("edit-portada").value,
  };

  try {
    const res = await fetch("/api/libro/editar", {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(libroEditado)
    });
    const json = await res.json();
    alert(`Libro actualizado: ${json.titulo}`);
    form.style.display = "none";
  } catch (err) {
    alert(err);
  }
});

// ===== Cargar lista de libros =====
let todosLosLibros = []; // se guarda la lista completa

async function cargarLibros() {
  const res = await fetch("/api/libros");
  todosLosLibros = await res.json();
  mostrarLibros(todosLosLibros);
}

// Mostrar libros (filtrados u ordenados)
function mostrarLibros(lista) {
  const tbody = document.getElementById("libros");
  const contador = document.getElementById("contador");
  const añadidor = document.getElementById("añadidor");
  tbody.innerHTML = "";
  
  // Mostrar cantidad de resultados
  contador.textContent = `${lista.length} libro${lista.length !== 1 ? "s" : ""} encontrado${lista.length !== 1 ? "s" : ""}`;

  lista.forEach(b => {
    const fila = document.createElement("tr");
    fila.innerHTML = `
      <td data-label="Portada">${b.portada_url ? `<img src="${b.portada_url}" class="portada">` : `<img src="static/29302.png" class="portada">`}</td>
      <td data-label="Título">${b.titulo}</td>
      <td data-label="Autor">${b.autor}</td>
      <td data-label="Editorial">${b.editorial}</td>
      <td data-label="Año">${b.año}</td>
      <td data-label="ISBN">${b.isbn}</td>
    `;
    tbody.appendChild(fila);
  });
  añadidor.style.display = "none";
}


// Filtros interactivos
document.getElementById("buscador").addEventListener("input", filtrarLibros);
document.getElementById("ordenarPor").addEventListener("change", filtrarLibros);

function normalizarTexto(texto) {
  return texto
    .toString()
    .normalize("NFD") // separa las tildes de las letras
    .replace(/[\u0300-\u036f]/g, "") // elimina las tildes
    .replace(/[^\w\s]/gi, "") // elimina cualquier carácter no alfanumérico (signos, puntuación, etc.)
    .toLowerCase()
    .trim();
}


function filtrarLibros() {
  const input = normalizarTexto(document.getElementById("buscador").value);
  
  const librosFiltrados = todosLosLibros.filter(libro =>
    normalizarTexto(libro.titulo).includes(input) ||
    normalizarTexto(libro.autor).includes(input) ||
    normalizarTexto(libro.editorial).includes(input)
  );

  // ordenar los resultados filtrados con el mismo criterio actual
  const criterio = document.getElementById("ordenarPor").value;
  const librosOrdenados = [...librosFiltrados].sort((a, b) => {
    let valorA = normalizarTexto(a[criterio]?.toString() || "");
    let valorB = normalizarTexto(b[criterio]?.toString() || "");
    if (criterio === "año") return (parseInt(valorA) || 0) - (parseInt(valorB) || 0);
    return valorA.localeCompare(valorB);
  });

  mostrarLibros(librosOrdenados);
}

cargarLibros();
