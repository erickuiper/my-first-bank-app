// Mock implementation for codegenNativeComponent
export default function codegenNativeComponent(componentName, options) {
  return function MockComponent(props) {
    return null; // Return null for web
  };
}
