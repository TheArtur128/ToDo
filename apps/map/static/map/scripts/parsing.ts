export function getCurrentMapId(): number {
    return Number(window.location.pathname.split('/')[2]);
}
