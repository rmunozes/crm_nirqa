function cerrarModal() {
  document.getElementById("modal-edicion").style.display = "none";
  document.getElementById("modal-contenido").innerHTML = "";
}

// Crear nueva OC
function mostrarFormularioOC(idPropuesta) {
  fetch(`/facturacion/nueva_oc?id_propuesta=${idPropuesta}&ajax=1`)
    .then(res => res.text())
    .then(html => {
      document.getElementById("modal-contenido").innerHTML = html;
      document.getElementById("modal-edicion").style.display = "flex";
      const form = document.getElementById("modal-contenido").querySelector("form");
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
            const detalle = document.getElementById("detalles-" + idPropuesta);
            detalle.innerHTML = html;
            detalle.style.display = "block";
            cerrarModal();
          });
      });
    });
}

// Crear nueva Factura
function mostrarFormularioFactura(idPropuesta) {
  fetch(`/facturacion/factura/nueva?id_propuesta=${idPropuesta}&ajax=1`)
    .then(res => res.text())
    .then(html => {
      document.getElementById("modal-contenido").innerHTML = html;
      document.getElementById("modal-edicion").style.display = "flex";
      const form = document.getElementById("modal-contenido").querySelector("form");
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
            const detalle = document.getElementById("detalles-" + idPropuesta);
            detalle.innerHTML = html;
            detalle.style.display = "block";
            cerrarModal();
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
      document.getElementById("modal-contenido").innerHTML = html;
      document.getElementById("modal-edicion").style.display = "flex";
      const form = document.getElementById("modal-contenido").querySelector("form");
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
            const detalle = document.getElementById("detalles-" + idPropuesta);
            detalle.innerHTML = html;
            detalle.style.display = "block"; // ✅ ESTO EVITA LA DESAPARICIÓN
            cerrarModal();
          });
      });
    });
}
