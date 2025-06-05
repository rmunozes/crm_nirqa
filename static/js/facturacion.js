
function cerrarModal() {
  document.getElementById("modal-edicion").style.display = "none";
  document.getElementById("modal-contenido").innerHTML = "";

  // 🔁 Cierra también cualquier fila de detalles abierta
  document.querySelectorAll("[id^='detalles-']").forEach(el => {
    el.style.display = "none";
  });
}


// Crear nueva OC
function mostrarFormularioOC(idPropuesta) {
  fetch(`/facturacion/nueva_oc?id_propuesta=${idPropuesta}&ajax=1`)
    .then(res => res.text())
    .then(html => {
      const fila = document.getElementById("detalles-" + idPropuesta);
      const contenido = document.getElementById("modal-contenido");
      contenido.innerHTML = html;
      document.getElementById("modal-edicion").style.display = "flex";

      const form = contenido.querySelector("form");
      if (!form) {
        console.warn("⚠️ No se encontró formulario de creación de OC");
        return;
      }

      form.addEventListener("submit", function (e) {
        e.preventDefault();
        const formData = new FormData(form);
        fetch(`/facturacion/nueva_oc?id_propuesta=${idPropuesta}&ajax=1`, {
          method: "POST",
          body: formData
        }).then(res => res.text())
          .then(html => {
            if (fila) {
              fila.style.display = "table-row";
              fila.querySelector("td").innerHTML = html;
            }
            window.location.reload();

          });
      });
    });
}



// Crear nueva Factura
function mostrarFormularioFactura(idPropuesta) {
  fetch(`/facturacion/factura/nueva?id_propuesta=${idPropuesta}&ajax=1`)
    .then(res => res.text())
    .then(html => {
      const fila = document.getElementById("detalles-" + idPropuesta);
      const contenido = document.getElementById("modal-contenido");
      contenido.innerHTML = html;
      document.getElementById("modal-edicion").style.display = "flex";

      const form = contenido.querySelector("form");
      if (!form) {
        console.warn("⚠️ No se encontró formulario de creación de factura");
        return;
      }

      form.addEventListener("submit", function (e) {
        e.preventDefault();
        const formData = new FormData(form);
        fetch(`/facturacion/factura/nueva?id_propuesta=${idPropuesta}&ajax=1`, {
          method: "POST",
          body: formData
        }).then(res => res.text())
          .then(html => {
            if (fila) {
              fila.style.display = "table-row";
              fila.querySelector("td").innerHTML = html;
            }
            window.location.reload();

          });
      });
    });
}



// Editar OC
function mostrarFormularioEditarOC(idOc, idPropuesta) {
  fetch(`/facturacion/oc/editar/${idOc}?id_propuesta=${idPropuesta}&ajax=1`)
    .then(res => res.text())
    .then(html => {
      document.getElementById("modal-contenido").innerHTML = html;
      document.getElementById("modal-edicion").style.display = "flex";
      const form = document.getElementById("modal-contenido").querySelector("form");
      if (!form) {
        console.warn("⚠️ No se encontró formulario OC");
        return;
      }
      form.addEventListener("submit", function (e) {
        e.preventDefault();
        const formData = new FormData(form);
        fetch(`/facturacion/oc/editar/${idOc}?id_propuesta=${idPropuesta}&ajax=1`, {
          method: "POST",
          body: formData
        }).then(res => res.text())
          .then(html => {
            const detalle = document.getElementById("detalles-" + idPropuesta);
            detalle.innerHTML = html;
            detalle.style.display = "block";
            cerrarModal();
          });
      });
    });
}

// Editar Factura
function mostrarFormularioEditarFactura(idFactura, idPropuesta) {
  fetch(`/facturacion/factura/editar/${idFactura}?id_propuesta=${idPropuesta}&ajax=1`)
    .then(res => res.text())
    .then(html => {
      const fila = document.getElementById("detalles-" + idPropuesta);
      const contenido = document.getElementById("modal-contenido");
      contenido.innerHTML = html;
      document.getElementById("modal-edicion").style.display = "flex";

      const form = contenido.querySelector("form");
      if (!form) {
        console.warn("⚠️ No se encontró formulario de factura");
        return;
      }

      form.addEventListener("submit", function (e) {
        e.preventDefault();
        const formData = new FormData(form);
        fetch(`/facturacion/factura/editar/${idFactura}?id_propuesta=${idPropuesta}&ajax=1`, {
          method: "POST",
          body: formData
        }).then(res => res.text())
          .then(html => {
            if (fila) {
              fila.style.display = "table-row";
              fila.querySelector("td").innerHTML = html;
            }
            cerrarModal();
          });
      });
    });
}

function toggleDetalles(id) {
  const fila = document.getElementById("detalles-" + id);
  const contenido = document.getElementById("contenido-" + id);

  if (fila.style.display === "none") {
    // 🔁 Cierra todos los detalles visibles antes de abrir uno nuevo
    document.querySelectorAll("[id^='detalles-']").forEach(el => {
      el.style.display = "none";
    });

    fetch("/facturacion/propuesta/" + id + "?ajax=1")
      .then(res => res.text())
      .then(html => {
        contenido.innerHTML = html;
        fila.style.display = "table-row";
      });
  } else {
    fila.style.display = "none";
  }
}
