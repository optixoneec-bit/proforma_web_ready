(function(){
  const body = document.getElementById("items-body");
  const btnAdd = document.getElementById("btn-add");
  const hidden = document.getElementById("hidden-inputs");
  const form = document.getElementById("pf-form");

  function currency(n){ return `$${Number(n||0).toFixed(2)}` }

  function recalc(){
    let subtotal = 0;
    [...body.querySelectorAll("tr")].forEach(tr=>{
      const p = parseFloat(tr.querySelector(".it-precio")?.value || 0);
      const c = parseInt(tr.querySelector(".it-cant")?.value || 0);
      const sub = p * c;
      tr.querySelector(".it-sub").innerText = currency(sub);
      subtotal += sub;
    });
    const iva = +(subtotal * 0.12).toFixed(2);
    const total = +(subtotal + iva).toFixed(2);
    document.getElementById("ui-subtotal").innerText = currency(subtotal);
    document.getElementById("ui-iva").innerText = currency(iva);
    document.getElementById("ui-total").innerHTML = `<strong>${currency(total)}</strong>`;
  }

  function addRow(desc, precio, cant){
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td><input class="form-control it-desc" value="${desc||''}" placeholder="Descripción"></td>
      <td><input class="form-control it-precio" type="number" step="0.01" value="${precio||''}" placeholder="0.00"></td>
      <td><input class="form-control it-cant" type="number" step="1" min="1" value="${cant||1}"></td>
      <td class="it-sub text-muted">—</td>
      <td><button class="btn btn-sm btn-outline-danger btn-del" type="button">Eliminar</button></td>
    `;
    body.appendChild(tr);
    tr.querySelector(".it-precio").addEventListener("input", recalc);
    tr.querySelector(".it-cant").addEventListener("input", recalc);
    tr.querySelector(".btn-del").addEventListener("click", ()=>{ tr.remove(); recalc(); });
    recalc();
  }

  btnAdd?.addEventListener("click", ()=>{
    const d = document.getElementById("new-desc").value.trim();
    const p = document.getElementById("new-precio").value;
    const c = document.getElementById("new-cant").value;
    if(!d || !p){ alert("Ingresa descripción y precio"); return; }
    addRow(d, p, c);
    document.getElementById("new-desc").value = "";
    document.getElementById("new-precio").value = "";
    document.getElementById("new-cant").value = 1;
  });

  form?.addEventListener("submit", (e)=>{
    hidden.innerHTML = "";
    const rows = [...body.querySelectorAll("tr")];
    if(rows.length === 0){
      e.preventDefault();
      alert("Agrega al menos un ítem");
      return;
    }
    rows.forEach(tr=>{
      const d = tr.querySelector(".it-desc").value.trim();
      const p = tr.querySelector(".it-precio").value;
      const c = tr.querySelector(".it-cant").value;
      const inD = document.createElement("input");
      inD.type="hidden"; inD.name="item_descripcion[]"; inD.value=d; hidden.appendChild(inD);
      const inP = document.createElement("input");
      inP.type="hidden"; inP.name="item_precio[]"; inP.value=p; hidden.appendChild(inP);
      const inC = document.createElement("input");
      inC.type="hidden"; inC.name="item_cantidad[]"; inC.value=c; hidden.appendChild(inC);
    });
  });

  addRow("", "", 1);
})();