# Guía de estilo: visualización de datos y data storytelling

Una guía general para convertir cualquier conjunto de datos en gráficos claros y en una historia que se entienda en segundos. El estilo de referencia es el de **The Economist** y **The Wall Street Journal**: sobrio, directo, con un solo color que manda y textos que dicen la conclusión.

Sirve para carruseles (LinkedIn, Instagram), presentaciones, reportes y dashboards.

---

## 1. Principios

1. **Una lámina, una idea.** Cada gráfico responde una sola pregunta. Si hay dos ideas, son dos láminas.
2. **El título es la conclusión.** El lector debe entender el hallazgo sin mirar el gráfico.
3. **El dato manda, el diseño acompaña.** Nada decorativo que no ayude a leer el número.
4. **Un solo color de énfasis.** El resto en tonos neutros o en un color secundario apagado.
5. **Etiquetas directas, no leyendas.** El nombre de la serie va pegado a la línea o barra.
6. **Honestidad antes que impacto.** Si un dato tiene salvedades, se dicen en la nota al pie. Nunca se esconden métricas que contradicen la tesis.
7. **Contexto siempre.** Un número solo no dice nada; compáralo con algo (el año anterior, el promedio, un rival, una meta).

---

## 2. Anatomía de una lámina

De arriba hacia abajo, siempre en el mismo lugar:

| Elemento | Qué es | Ejemplo |
|---|---|---|
| **Kicker / etiqueta** | 1 a 4 palabras en mayúsculas que dicen el tema | `VENTAS 2025` |
| **Título** | La conclusión, como frase completa | "Las ventas online superaron a las de tienda por primera vez" |
| **Subtítulo (dek)** | Qué se está midiendo y cómo leer el gráfico | "Ingresos mensuales por canal, en millones de soles, 2020–2025." |
| **Gráfico** | El cuerpo de la lámina, con anotaciones | — |
| **Nota al pie** | Definiciones, salvedades, cortes de fecha, créditos de fotos | "Excluye devoluciones. Datos hasta el 30 de septiembre." |
| **Pie de fuente** | Fuente de los datos, una línea | "Fuente: INEI, reportes internos" |
| **Número de página** | Para carruseles | `03/12` |

### Reglas del título

- Es una **afirmación verdadera para todo el gráfico**, no una descripción. Evita "Ventas por canal"; escribe "El canal online creció 3 veces en cinco años".
- Máximo **2 líneas**. Si necesita 3, la idea es demasiado compleja o el texto está inflado.
- Incluye **el número clave** cuando se pueda: "18 goles en 2022", "+34% en un año".
- Misma gramática en todo el documento: todas afirmaciones, sin mezclar preguntas y frases sueltas (salvo una lámina de pregunta intencional).
- Sin dramatismo vacío ("No es X, es Y", "Lo que nadie te cuenta…").

### Reglas del subtítulo

- Dice **qué** se mide, **en qué unidad**, **qué periodo** y **cómo leer** el gráfico si no es obvio ("Cada punto es un partido", "Cada fila tiene su propia escala").
- 1 a 2 líneas. No repite el título.

### Reglas de la nota al pie

- Todo lo que el lector escéptico preguntaría: definiciones, exclusiones, datos faltantes, fuentes con criterios distintos, corte de fecha, si un actor sigue activo.
- Créditos de fotos e imágenes con su licencia.
- Tamaño pequeño y color gris, pero legible.

---

## 3. Tipografía

Tres familias como máximo, cada una con un trabajo:

| Rol | Tipo de letra | Uso |
|---|---|---|
| **Display** | Condensada y pesada (ej. Anton, Oswald, Bebas) | Títulos en MAYÚSCULAS, números grandes |
| **Texto** | Sans legible (ej. Barlow, Inter, Source Sans) | Subtítulos, párrafos, notas |
| **Etiquetas** | Condensada ligera (ej. Barlow Condensed, Roboto Condensed) | Ejes, valores en barras, kicker, leyendas, nombres |

### Escala de tamaños (referencia para lienzo 1080 × 1350 px)

| Elemento | Tamaño | Peso |
|---|---|---|
| Titular de portada | 100–130 px | Display |
| Número grande (KPI) | 130–160 px | Display |
| Título de lámina | 54–66 px | Display, mayúsculas |
| Subtítulo | 30–32 px | Regular, gris oscuro |
| Texto de cuerpo / anotaciones | 22–28 px | Regular |
| Etiquetas de valor | 22–30 px | Bold |
| Ticks de ejes | 22–24 px | Regular, gris |
| Kicker | 26–30 px | Bold, mayúsculas, espaciado +1 a +2 px |
| Nota al pie / fuente | 20–24 px | Regular, gris |

Nada por debajo de **20 px** en un carrusel: en un teléfono no se lee.

Para 16:9 (1920 × 1080) multiplica aproximadamente por 1,3.

### Reglas

- Títulos en **mayúsculas** solo con la fuente display.
- Énfasis con **peso o color**, no con un tamaño nuevo.
- Interlineado: 1,0–1,1 en títulos; 1,25–1,35 en texto.

---

## 4. Color

### Paleta por roles (no por gusto)

| Rol | Uso | Ejemplo |
|---|---|---|
| **Fondo** | Blanco o casi blanco | `#FFFFFF` |
| **Texto principal** | Casi negro | `#111111` |
| **Texto secundario** | Gris oscuro / medio | `#4A4A4A`, `#666666` |
| **Énfasis (highlight)** | El dato o sujeto protagonista. Uno solo. | Amarillo, rojo o naranja de marca |
| **Serie de comparación** | El resto de las series | Azul suave o gris |
| **Contexto / apagado** | Series secundarias en gráficos de líneas | Gris claro `#BDBDBD` |
| **Líneas de cuadrícula** | Muy sutiles | `#E3E3E3` |
| **Banda de cabecera / pie** | Identidad del documento | Color de marca y negro |

### Reglas

- **El color de énfasis se reserva** para el protagonista o el dato clave de la lámina. Si todo está resaltado, nada lo está.
- Formas en color claro sobre fondo blanco llevan **contorno fino oscuro** (1–1,5 px) para que se lean.
- Los colores que deben distinguirse cambian también en **luminosidad**, no solo en tono. Prefiere azul/naranja a rojo/verde (daltonismo).
- **El color nunca habla solo**: si una barra es "la ganadora", también lo dice el texto o la etiqueta.
- Bandas de fondo muy suaves (ej. `#EEF4FA`) para marcar periodos o regiones del gráfico.

---

## 5. Números

### Formato

- **Separador decimal según el idioma.** En español: coma decimal (`0,61`, `64,9%`). En inglés: punto.
- **Separador de miles** solo con 5+ dígitos y según el idioma (`12.500` en español, `12,500` en inglés).
- **Decimales consistentes por métrica**: si un promedio lleva 2 decimales, todos los de esa serie también.
  - Porcentajes: 0–1 decimal.
  - Ratios / promedios: 2 decimales.
  - Conteos: sin decimales.
- **Unidades explícitas**: en el subtítulo ("en millones de soles") o pegadas al valor (`72,8%`, `S/ 1,2 M`).
- Abreviaciones claras y consistentes: `PJ`, `G`, `A`, `M`, `K`. Explícalas una vez en el subtítulo o la nota.

### Dónde van

- **Etiqueta directa al final de cada barra**, fuera de la barra, en bold.
- Si la barra es muy corta, la etiqueta va igual afuera; nunca encimada.
- En gráficos de líneas, el valor final va al final de la línea junto al nombre (`Haaland · 19`).
- Los números clave de la historia se repiten en una **anotación** con una frase corta.

### Cuadro de KPIs (números grandes)

- 2 × 2 o 1 × 3 tarjetas.
- Número enorme + etiqueta corta + una línea de contexto ("récord", "1 cada 3,1 partidos").
- **Una sola tarjeta** con el color de énfasis.

---

## 6. Ejes y cuadrícula

- **Las barras empiezan en cero.** Siempre. Una barra truncada exagera diferencias.
- Las líneas pueden no empezar en cero si la variación es el foco, pero el eje debe dejarlo claro.
- **Cuadrícula horizontal** muy tenue; sin cuadrícula vertical salvo en scatter.
- La **línea de base (cero)** más gruesa y oscura que el resto.
- **Pocos ticks**: 4 a 6 por eje, en números redondos (0, 5, 10, 15, 20).
- En ejes de tiempo, no etiquetes cada año: cada 5 años, o solo los años relevantes.
- Sin títulos de eje si el subtítulo ya explica la unidad. Si hacen falta, cortos y en gris.
- Sin bordes de gráfico, sin sombras, sin 3D.
- **Una escala por panel** en small multiples. Si cada fila tiene su propia escala, dilo en el subtítulo.

---

## 7. Qué gráfico usar

| Pregunta que respondes | Gráfico | Notas |
|---|---|---|
| ¿Cómo evolucionó algo en el tiempo? | **Columnas** (pocos periodos) o **línea** (muchos periodos) | Resalta el pico o el año clave |
| ¿Quién es mayor / menor? | **Barras horizontales ordenadas** de mayor a menor | Nombres largos caben mejor en horizontal |
| ¿Antes vs. después? ¿A vs. B? | **Barras pareadas**, **dumbbell** o **butterfly** (espejo) | Una escala por métrica si las unidades difieren |
| ¿Cómo se compone un total? | **Barra apilada al 100%** horizontal | Evita tortas con más de 3 partes |
| ¿Dos métricas a la vez? | **Scatter / burbujas** con líneas de promedio y cuadrantes rotulados | El tamaño de burbuja puede ser una tercera variable |
| ¿Cómo se distribuyen los valores? | **Histograma**, **beeswarm** o **campana** con la curva normal superpuesta | Marca media y ±1 o ±2 desviaciones estándar |
| ¿Cada evento individual importa? | **Unit chart / dot matrix** (un punto = un caso) | Muy humano: "cada punto es un partido" |
| ¿Ganancias y pérdidas en el mismo eje? | **Barras divergentes** (arriba / abajo del cero) | Arriba lo positivo, abajo lo negativo |
| ¿Cuándo pasó cada cosa? | **Línea de tiempo** con hitos, o **strip plot** de eventos por fila | Usa formas distintas por tipo de evento + leyenda |
| ¿Varias categorías con la misma métrica? | **Small multiples** (paneles 2 × 2) | Mismo tamaño y estilo en cada panel |
| ¿Cómo cambió un ranking? | **Slope chart** o líneas con etiqueta al final | Resalta 1 o 2 líneas, el resto en gris |

### Para no aburrir en un carrusel

- No pongas dos gráficos del mismo tipo seguidos. Alterna barras, líneas, scatter, puntos, línea de tiempo y números grandes.
- Intercala láminas de **texto con pregunta** o **números grandes** entre láminas de gráficos para dar respiro.

---

## 8. Anotaciones (lo que convierte un gráfico en historia)

- Anota **directamente** el dato clave: una etiqueta en bold + una frase corta en gris ("2022: 18 goles en 14 partidos. El 14% de toda su carrera en un año").
- Usa **líneas guía** finas (1–1,5 px) cuando la anotación no esté pegada al punto.
- **Líneas de referencia punteadas** para promedios o metas, rotuladas ("prom. 0,58", "meta 100%").
- **Bandas de fondo** para periodos ("tras la vuelta", "pandemia").
- Rótulos de cuadrante en mayúsculas y gris en los scatter ("MARCA Y ASISTE", "GOLEADOR PURO").
- Máximo **2–3 anotaciones** por gráfico. Más que eso, ruido.
- Las anotaciones nunca tapan datos: si chocan, muévelas a espacio vacío.

---

## 9. Espaciado y layout

### Formatos

| Uso | Tamaño | Proporción |
|---|---|---|
| Carrusel LinkedIn / Instagram | 1080 × 1350 px | 4:5 |
| Post cuadrado | 1080 × 1080 px | 1:1 |
| Presentación | 1920 × 1080 px | 16:9 |

### Márgenes y rejilla (para 1080 × 1350)

- Márgenes laterales: **64 px**.
- Banda superior (cabecera con kicker): ~96 px.
- Banda inferior (fuente + página): ~78 px.
- Separación título → subtítulo: ~18 px. Subtítulo → gráfico: ~28 px.
- El gráfico ocupa **60–70%** de la altura útil.
- Los elementos repetidos (título, kicker, fuente, número de página) **siempre en la misma posición**, para que no "salten" al deslizar.

### Densidad

- Si una lámina se siente apretada, **divídela en dos**. No reduzcas la letra.
- Deja aire alrededor del dato principal. El vacío también guía la mirada.
- Revisa siempre: nada se superpone, nada se corta, nada sale del margen.

---

## 10. Imágenes y stickers

- Usa **fotos reales** con licencia libre (Wikimedia Commons, Unsplash) o propias, y acredítalas en la nota al pie.
- Recorta personas u objetos como **sticker** (contorno blanco + sombra suave) para dar contexto sin tapar datos.
- Las fotos que no se recortan bien van como **polaroid** (borde blanco, leve rotación).
- Las caras pueden ir **como marcadores** en un scatter o **junto al nombre** en un ranking.
- Nunca inventes una imagen que parezca real (ej. pegar un objeto en las manos de alguien). Si no existe la foto, usa dos stickers separados.
- Colócalos en zonas vacías: esquina superior derecha sobre la cabecera, al costado de un texto, nunca sobre barras o puntos.
- Pocos: 1 por lámina como máximo, y no en todas.

---

## 11. Estructura narrativa (storytelling)

### Arco básico para un carrusel de 10–16 láminas

1. **Portada (gancho):** titular fuerte con 2–3 números, una frase que promete la historia, una imagen protagonista.
2. **Panorama:** los números grandes que resumen todo (KPIs).
3. **Evolución:** cómo cambió en el tiempo (columnas / líneas).
4. **Profundidad:** una o dos láminas que explican el porqué (eficiencia, distribución, composición).
5. **Giro / pregunta:** una lámina con una pregunta clara ("¿Valió la pena volver?").
6. **Respuesta:** la evidencia que contesta la pregunta, en la lámina siguiente, con el mismo lenguaje.
7. **Comparación:** contra pares, rivales o benchmarks.
8. **Cierre:** 3–4 conclusiones numeradas + una frase final que responda la gran pregunta.

### Reglas de narración

- **Pregunta → respuesta** deben leerse como una conversación: la pregunta anuncia qué se va a comparar; la respuesta usa las mismas palabras ("antes de renunciar" / "después de volver").
- No repitas la misma palabra de énfasis en título y recuadro (si el recuadro dice "SÍ.", el título no empieza con "Sí:").
- No pongas "desliza" ni "en la siguiente lámina": cada lámina debe entenderse sola.
- Usa **todo el dataset**, no un solo ángulo: tiempo, comparación, distribución, composición.
- Muestra también los datos que no favorecen tu tesis; luego explica por qué la tesis se sostiene. Da más credibilidad.
- El cierre puede tomar postura ("los datos dicen que sí"), pero acotada a lo que los datos cubren.

---

## 12. Rigor y honestidad con los datos

Antes de diseñar, revisa los datos:

- [ ] Los totales cuadran con la suma de las partes (por año, por categoría).
- [ ] Los porcentajes y promedios están recalculados, no copiados.
- [ ] Los datos recientes están verificados con fuentes externas (prensa, sitios oficiales).
- [ ] Está claro qué incluye y qué excluye cada métrica.
- [ ] Si las fuentes usan criterios distintos, se dice en la nota.
- [ ] Si un dato no existe oficialmente, se busca el mejor conteo disponible y se cita, en vez de dejar un hueco.

Cuidado con:

- **Sesgo de muestra:** comparar promedios entre casos con muy distinta cantidad de observaciones (92 vs. 234). Prefiere totales, o aclara el tamaño de muestra.
- **Escalas engañosas:** barras sin cero, ejes duales, escalas distintas sin aviso.
- **Selección de métricas:** si comparas en 8 métricas y ganas en 5, muestra las 8.
- **Fechas de corte:** si algo sigue cambiando (alguien sigue activo, el año no terminó), dilo.

---

## 13. Pie de fuente y créditos

- Formato: `Fuente: [organización 1], [organización 2] · [aclaración corta]`
- Una sola línea; si no cabe, abrevia las fuentes y mueve el detalle a la nota al pie.
- No pongas tu usuario ni llamadas a seguir en el pie de un contenido informativo.
- Las fotos llevan `Foto: Autor (licencia)` en la nota al pie.

---

## 14. Checklist final antes de publicar

**Contenido**
- [ ] Cada título es una conclusión verdadera y verificable.
- [ ] Cada subtítulo explica qué se mide, la unidad y el periodo.
- [ ] Ningún gráfico se repite en tipo dos veces seguidas.
- [ ] La pregunta y su respuesta usan el mismo lenguaje.
- [ ] El cierre resume en 3–4 puntos y responde la gran pregunta.

**Datos**
- [ ] Todos los números revisados y consistentes entre láminas.
- [ ] Decimales y separadores según el idioma.
- [ ] Salvedades en notas al pie.
- [ ] Fuentes citadas.

**Diseño**
- [ ] Un solo color de énfasis por lámina.
- [ ] Barras desde cero.
- [ ] Etiquetas directas, sin leyendas innecesarias.
- [ ] Nada se superpone ni se corta.
- [ ] Texto mínimo de 20 px.
- [ ] Elementos repetidos en la misma posición en todas las láminas.
- [ ] Imágenes con crédito y licencia.

**Formato**
- [ ] Exportado en el tamaño correcto (4:5 para carrusel).
- [ ] PDF con título de documento descriptivo (LinkedIn lo muestra).
- [ ] PNG por lámina para Instagram.
