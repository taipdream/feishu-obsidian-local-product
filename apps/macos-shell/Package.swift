// swift-tools-version: 5.10
import PackageDescription

let package = Package(
    name: "macos-shell",
    platforms: [.macOS(.v14)],
    products: [
        .executable(name: "FeishuObsidianLocal", targets: ["App"])
    ],
    targets: [
        .executableTarget(name: "App"),
        .testTarget(name: "AppTests", dependencies: ["App"])
    ]
)
