import { createReadStream } from "node:fs"
import { createServer } from "node:http"
import { fileURLToPath } from "node:url"

const reportPath = fileURLToPath(
  new URL("../reports/evidence-dashboard.html", import.meta.url),
)
const vectorPath = fileURLToPath(
  new URL("../assets/evidence/evaluation-success.svg", import.meta.url),
)

createServer((request, response) => {
  if (request.url === "/evaluation-success.svg") {
    response.writeHead(200, {
      "Content-Type": "image/svg+xml; charset=utf-8",
      "Cache-Control": "no-store",
    })
    createReadStream(vectorPath).pipe(response)
    return
  }
  if (request.url !== "/" && request.url !== "/evidence-dashboard.html") {
    response.writeHead(404, { "Content-Type": "text/plain; charset=utf-8" })
    response.end("Not found")
    return
  }
  response.writeHead(200, {
    "Content-Type": "text/html; charset=utf-8",
    "Cache-Control": "no-store",
  })
  createReadStream(reportPath).pipe(response)
}).listen(8094, "127.0.0.1", () => {
  console.log("Evidence dashboard: http://127.0.0.1:8094/")
})
