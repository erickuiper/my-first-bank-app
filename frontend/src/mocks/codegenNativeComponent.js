// Mock implementation for codegenNativeComponent
export default function codegenNativeComponent(_componentName, _options) {
  return function MockComponent(_props) {
    return null; // Return null for web
  };
}
