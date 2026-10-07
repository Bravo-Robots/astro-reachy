const data = {
  sun: [
    "SOL",
    "ESTRELLA // CENTRO DEL SISTEMA SOLAR",
    "SOL_001",
    "CENTRO DEL SISTEMA",
    "1.392.700 KM",
    "—",
    "27,9 G",
    "—",
    "5.505 °C",
    "0",
    "HIDRÓGENO + HELIO",
    "¡Has encontrado el Sol! Es la estrella que ilumina y calienta nuestro hogar.",
  ],
  mercury: [
    "MERCURIO",
    "PLANETA ROCOSO // PRIMER PLANETA",
    "MERCURIO_001",
    "57,9 M KM",
    "4.879 KM",
    "58,6 DÍAS",
    "0,38 G",
    "88 DÍAS",
    "−180 / 430 °C",
    "0",
    "EXOSFERA MUY TENUE",
    "¡Has encontrado Mercurio, el planeta más cercano al Sol! Su año dura apenas 88 días terrestres.",
  ],
  venus: [
    "VENUS",
    "PLANETA ROCOSO // SEGUNDO PLANETA",
    "VENUS_001",
    "108,2 M KM",
    "12.104 KM",
    "243 DÍAS",
    "0,9 G",
    "224,7 DÍAS",
    "464 °C",
    "0",
    "CO₂ Y ÁCIDO SULFÚRICO",
    "¡Has encontrado Venus! Es parecido a la Tierra en tamaño, pero es el planeta más caliente.",
  ],
  earth: [
    "TIERRA",
    "PLANETA ROCOSO // NUESTRO HOGAR",
    "TIERRA_001",
    "149,6 M KM",
    "12.742 KM",
    "24 HORAS",
    "1 G",
    "365,25 DÍAS",
    "15 °C",
    "1",
    "NITRÓGENO + OXÍGENO",
    "¡Has encontrado la Tierra, nuestro planeta! Sus océanos cubren cerca del 71 por ciento de la superficie.",
  ],
  moon: [
    "LUNA",
    "SATÉLITE NATURAL // TIERRA",
    "LUNA_001",
    "384.400 KM",
    "3.475 KM",
    "27,3 DÍAS",
    "0,165 G",
    "27,3 DÍAS",
    "−173 / 127 °C",
    "0",
    "EXOSFERA MUY TENUE",
    "¡Has encontrado la Luna, el satélite natural de la Tierra! Siempre nos muestra casi la misma cara.",
  ],
  mars: [
    "MARTE",
    "PLANETA ROCOSO // CUARTO PLANETA",
    "MARTE_001",
    "227,9 M KM",
    "6.779 KM",
    "24 H 39 MIN",
    "0,38 G",
    "687 DÍAS",
    "−63 °C",
    "2",
    "CO₂ // MUY TENUE",
    "¡Has encontrado Marte, el planeta rojo! Su color se debe a minerales de hierro oxidados.",
  ],
  jupiter: [
    "JÚPITER",
    "GIGANTE GASEOSO // QUINTO PLANETA",
    "JUPITER_001",
    "778,5 M KM",
    "139.820 KM",
    "CASI 10 HORAS",
    "2,53 G",
    "11,86 AÑOS",
    "−110 °C",
    "95",
    "HIDRÓGENO + HELIO",
    "¡Has encontrado Júpiter, el gigante del Sistema Solar! Por volumen podrían caber más de mil Tierras.",
  ],
  saturn: [
    "SATURNO",
    "GIGANTE GASEOSO // SEXTO PLANETA",
    "SATURNO_001",
    "1.432 M KM",
    "116.460 KM",
    "10,7 HORAS",
    "1,07 G",
    "29,45 AÑOS",
    "−140 °C",
    "146",
    "HIDRÓGENO + HELIO",
    "¡Has encontrado Saturno, el planeta de los anillos! Sus anillos están formados por incontables fragmentos de hielo, roca y polvo.",
  ],
  uranus: [
    "URANO",
    "GIGANTE HELADO // SÉPTIMO PLANETA",
    "URANO_001",
    "2.871 M KM",
    "50.724 KM",
    "17 HORAS",
    "0,89 G",
    "84 AÑOS",
    "−195 °C",
    "28",
    "HIDRÓGENO, HELIO, METANO",
    "¡Has encontrado Urano, un gigante helado de color azul verdoso que gira tumbado.",
  ],
  neptune: [
    "NEPTUNO",
    "GIGANTE HELADO // OCTAVO PLANETA",
    "NEPTUNO_001",
    "4.495 M KM",
    "49.244 KM",
    "16 HORAS",
    "1,14 G",
    "164,8 AÑOS",
    "−200 °C",
    "16",
    "HIDRÓGENO, HELIO, METANO",
    "¡Has encontrado Neptuno, el planeta más lejano del Sistema Solar y hogar de vientos extremos.",
  ],
};
const get = (id) => document.getElementById(id),
  app = get("app");
function identify(key) {
  const p = data[key];
  app.classList.add("acquiring");
  get("scan-status").textContent = "ADQUIRIENDO OBJETIVO...";
  get("scan-detail").textContent = "SEÑAL QR // BLOQUEADA";
  get("guide-status").textContent = "ANALIZANDO QR";
  setTimeout(() => {
    app.classList.remove("acquiring");
    app.classList.add("speaking");
    get("scan-status").textContent = "OBJETIVO IDENTIFICADO";
    get("scan-detail").textContent = `${p[2]} // BASE DE DATOS ONLINE`;
    get("guide-status").textContent = "REACHY ESTÁ HABLANDO";
    get("guide-quote").textContent = `“Preparando la misión de ${p[0]}.”`;
    [
      ["name", 0],
      ["kind", 1],
      ["code", 2],
      ["distance", 3],
      ["diameter", 4],
      ["day", 5],
      ["gravity", 6],
      ["year", 7],
      ["temp", 8],
      ["moons", 9],
      ["atmosphere", 10],
      ["story", 11],
    ].forEach(
      ([id, n]) => (get(id).textContent = id === "story" ? `“${p[n]}”` : p[n]),
    );
    get("planet-visual").className = `planet-visual ${key}`;
    document
      .querySelectorAll(".objects button")
      .forEach((b) => b.classList.toggle("selected", b.dataset.planet === key));
    get("ficha").scrollIntoView({ behavior: "smooth", block: "center" });
  }, 620);
}
document
  .querySelectorAll(".objects button")
  .forEach((b) =>
    b.addEventListener("click", () => identify(b.dataset.planet)),
  );
get("demo-scan").addEventListener("click", () => identify("saturn"));
document.addEventListener("pointermove", (e) => {
  if (matchMedia("(prefers-reduced-motion: reduce)").matches) return;
  const s = document.querySelector(".solar");
  s.style.transform = `translate(${(e.clientX / innerWidth - 0.5) * 5}px,${(e.clientY / innerHeight - 0.5) * 5}px)`;
});
