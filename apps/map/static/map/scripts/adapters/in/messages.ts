export async function asyncAlert(message: string): Promise<void> {
    await alert(message);
}
