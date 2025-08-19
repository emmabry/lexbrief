function Error({ error }: { error: string | null }) {
    return (
        <div className="error d-flex flex-column justify-content-center align-items-center">
        <h1 className="text-danger">Error</h1>
        <p className="text-secondary">{error}</p>
        </div>
    );
}

export default Error;