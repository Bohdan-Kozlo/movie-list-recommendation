type CatalogueMessageProps = {
  title: string
  body: string
}

export function CatalogueMessage({ title, body }: CatalogueMessageProps) {
  return (
    <div className="message">
      <h2>{title}</h2>
      <p>{body}</p>
    </div>
  )
}
