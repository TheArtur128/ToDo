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
