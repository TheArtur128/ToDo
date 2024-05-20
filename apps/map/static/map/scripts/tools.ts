export type StorageHTMLElement = HTMLElement & {value: string}

export function isInDOMOf(
    treeElement: HTMLElement,
    searchElement: any,
): boolean {
    if (treeElement === searchElement)
        return true;

    const tree = document.createNodeIterator(treeElement, NodeFilter.SHOW_ALL);

    let node: Node | null;
    while (node = tree.nextNode())
        if (node === searchElement)
            return true;

    return false;
}

export function getCookies(): Record<string, string> {
    const cookies: Record<string, string> = {};

    for (let keyAndValueLine of document.cookie.replaceAll(' ', '').split(";")) {
        let [key, value] = keyAndValueLine.split("=");
        cookies[key] = value;
    }

    return cookies;
}

export const originalCookies = getCookies();
