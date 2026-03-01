## 1. Código de Conducta

Este proyecto y todos los que participan en él se rigen por un [Código de Conducta](CODE_OF_CONDUCT.md). 
Al participar, se espera que respetes este código. En resumen:
- Sé respetuoso y empático.
- Proporciona retroalimentación constructiva.
- Enfócate en lo que es mejor para la comunidad.

Si observas comportamientos inaceptables, por favor contacta de forma privada con los mantenedores del proyecto.

## 2. Contributor License Agreement (CLA) y DCO

Para que podamos aceptar tus contribuciones, sigue el estándar de *Developer Certificate of Origin* (DCO).  
Añade un sign-off a todos tus commits. Si usas git, simplemente añade la flag `-s` o `--signoff`:

```bash
git commit -s -m "Mensaje de commit claro y descriptivo"
```
Esto certifica que tienes el derecho de enviar el código bajo la licencia de este repositorio.

## 3. ¿Cómo puedo contribuir?

No solo necesitamos código. Existen muchas formas de contribuir y todas son igual de valiosas:

### 3.1. Reportando Bugs (Errores)

Antes de crear una *Issue*, busca en las issues existentes para asegurarte de que alguien no lo haya reportado ya. Si no existe, crea una nueva *Issue* detallando:
- **Resumen:** Descripción concisa del problema.
- **Entorno:** Versión del SO, Python, dependencias.
- **Pasos para reproducir:** Instrucciones paso a paso.
- **Resultados esperados vs actuales.**

### 3.2. Proponiendo Nuevas Funcionalidades

Si tienes una idea, ¡queremos escucharla! Abre una *Issue* describiendo:
- **Problema:** ¿Qué problema resuelve tu idea?
- **Solución propuesta:** ¿Cómo debería funcionar?
- **Alternativas consideradas:** ¿Hay otras aproximaciones?

### 3.3. Documentación

La documentación siempre se puede mejorar. Puedes contribuir arreglando errores tipográficos, aclarando textos, o añadiendo ejemplos de código e imágenes.

### 3.4. Primeros Pasos (Good First Issues)

Si es tu primera vez contribuyendo, busca el tag `good first issue` en nuestro rastreador de *Issues*. Son tareas especialmente seleccionadas para no requerir un conocimiento profundo de la arquitectura y que te ayudarán a familiarizarte con nuestro flujo de trabajo.

## 4. Configurando tu Entorno de Desarrollo Local

Para compilar y testear de forma local:
1. Haz un **fork** del repositorio a tu cuenta.
2. Clona tu fork: `git clone https://github.com/hackudc-Inditex/hackudc.git`
3. Instala las dependencias en un entorno virtual (`.venv` recomendado).
4. Verifica que los tests y linters se ejecutan sin errores antes de empezar.

## 5. Proceso de Pull Request (PR)

1. **Crea una rama (branch):** 
   - Nómbrala según su propósito: `feature/nombre-funcionalidad`, `fix/solucion-bug`, o `docs/actualiza-readme`.
2. **Haz tus cambios:**
   - Mantén los commits lógicos y separados. Usa mensajes de commit en formato imperativo, por ejemplo: _"Añade soporte para descargas asíncronas"_.
3. **Pasa los Tests y Linters:**
   - Asegúrate de que el código formatado cumple con los estándares del proyecto (por ejemplo, Black para Python).
4. **Envía el PR a la rama principal (`main`):**
   - Rellena la plantilla de PR. Linkea cualquier *Issue* relacionado (ej. "Cierra #42").
5. **Revisión (Code Review):**
   - Los mantenedores revisarán tu código. Si te sugieren cambios, por favor hazlos en esa misma rama y actualiza el PR con un `git push`. La colaboración y el diálogo abierto durante el Code Review es una parte vital para tener un proyecto de "clase mundial".

## 6. Canales de Comunicación

Si tienes una duda que no encaja en una issue de código y necesitas hablar con otros colaboradores o con los *core maintainers*:
- Abre una Issue con la etiqueta question.
- Abre un hilo de consultas antes de empezar un desarrollo masivo si en tu PR vas a tocar elementos vitales del núcleo del proyecto.

---
_¡Gracias de nuevo por ayudarnos a ser y seguir siendo un proyecto de código abierto de clase mundial!_
