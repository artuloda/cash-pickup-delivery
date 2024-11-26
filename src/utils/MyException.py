import functools
import traceback
import inspect


class MyException:
    def __init__(self, logger):
        self.logger = logger

    def exception_handler_decorator(self, method):
        """Decorator to handle exceptions in individual methods."""
        @functools.wraps(method)
        def wrapper(*args, **kwargs):
            try:
                return method(*args, **kwargs)
            except Exception as e:
                if not hasattr(e, "__handled__"):
                    e.__handled__ = True

                    module_name = method.__module__
                    method_name = method.__name__

                    class_name = None
                    if args and hasattr(args[0], "__class__"):
                        cls = args[0].__class__
                        if inspect.getmodule(cls).__name__ == module_name:
                            class_name = cls.__name__
                    full_traceback = traceback.format_exc()                   
                    # Construct the log message
                    if class_name:
                        log_message = f"Exception in module: {module_name}, class: {class_name}, method: {method_name}: {e}"
                    else:
                        log_message = f"Exception in module: {module_name}, method: {method_name}: {e}"

                    # Log the full traceback and the error message
                    self.logger.error(full_traceback)
                    self.logger.error(log_message)
                raise

        return wrapper

    def decorate_methods(self, instance):
        """Function to decorate all methods of an instance with exception handling."""
        cls = instance.__class__
        for attr_name in dir(instance):
            if attr_name.startswith("__") and attr_name.endswith("__"):
                continue

            attr_value = getattr(instance, attr_name)
            if callable(attr_value):
                decorated_method = self.exception_handler_decorator(attr_value)
                setattr(instance, attr_name, decorated_method)

            cls_attr_value = getattr(cls, attr_name, None)
            if isinstance(cls_attr_value, staticmethod):
                original_func = cls_attr_value.__func__
                decorated_func = self.exception_handler_decorator(original_func)
                setattr(cls, attr_name, staticmethod(decorated_func))
            elif isinstance(cls_attr_value, classmethod):
                original_func = cls_attr_value.__func__
                decorated_func = self.exception_handler_decorator(original_func)
                setattr(cls, attr_name, classmethod(decorated_func))


