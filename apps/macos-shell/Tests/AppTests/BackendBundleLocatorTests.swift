import Testing
import Foundation
@testable import App

@Test
func testBackendBundleLocatorPrefersEmbeddedBackendBundle() {
    let locator = BackendBundleLocator(
        fileManager: .default,
        environment: [:],
        mainBundleResourceURL: URL(fileURLWithPath: "/tmp/Fake.app/Contents/Resources")
    )

    let result = locator.backendEntryPoint()

    #expect(
        result.path ==
        "/tmp/Fake.app/Contents/Resources/backend-bundle/run_backend"
    )
}
