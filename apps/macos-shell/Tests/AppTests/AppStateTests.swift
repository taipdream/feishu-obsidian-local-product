import Testing
@testable import App

@Test
func testDefaultVaultPathUsesDocumentsInsightVault() {
    let state = AppState()
    #expect(state.defaultVaultPath.hasSuffix("/Documents/InsightVault"))
}
