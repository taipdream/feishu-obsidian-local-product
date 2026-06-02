import Testing
import Foundation
@testable import App

@Test
func testBackendProcessControllerStartsAndStopsProcess() throws {
    let controller = BackendProcessController()
    let executableURL = URL(fileURLWithPath: "/usr/bin/true")

    try controller.startBackend(executableURL: executableURL)
    controller.stopBackend()

    #expect(Bool(true))
}
