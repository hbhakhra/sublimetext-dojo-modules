import sublime_plugin, sublime
import os, os.path, re
try:
	import modulecache
except:
	import DojoModules.modulecache as modulecache

module_cache = modulecache.ModuleCache()
settings_file = 'DojoModules.sublime-settings'
settings = sublime.load_settings(settings_file)

def load_dojo_module_cache():
	search_paths = settings.get('search_paths')
	if not search_paths:
		modulecache.log('WARNING: No search_paths have been set. See the README file for `Dojo Module Completions` for details.')
		return

	module_cache.scan_all_paths(search_paths)

settings.add_on_change('search_paths', load_dojo_module_cache)
load_dojo_module_cache()


class InsertDojoModuleCommand(sublime_plugin.TextCommand):
	"""Shows quick panel to insert a Dojo module name.

	These are the same modules as returned by the suggested completions.
	Provided as a way to bind a keyboard shortcut to this action instead of
	relying on completions.

	"""

	def is_enabled(self):
		for region in self.view.sel():
			if self.view.score_selector(region.a, 'source.js | text.html.basic'):
				return True
		return False

	def run(self, edit):
		modules = sorted(set(module_cache.modules))
		def on_done(i):
			if i == -1: return
			for region in self.view.sel():
				self.view.insert(edit, region.b, modules[i])
		self.view.window().show_quick_panel(modules, on_done)


class RequireDojoModuleCommand(sublime_plugin.TextCommand):
	"""Insert a Dojo module as part of a `dojo.require` statement."""

	def is_enabled(self):
		for region in self.view.sel():
			if self.view.score_selector(region.a, 'source.js'):
				return True
		return False

	def run(self, edit):
		modules = sorted(set(module_cache.modules))
		def on_done(i):
			if i == -1: return
			for region in self.view.sel():
				comment = settings.get('require_comment') or ""
				self.view.insert(edit, region.b, ("dojo.require('%s');" + comment) % (modules[i]))
		self.view.window().show_quick_panel(modules, on_done)


class DojoModuleCompletions(sublime_plugin.EventListener):
	"""Provides completions for all the scanned Dojo modules."""

	def on_post_save(self, view):
		saved_file = view.file_name()	
		if any(saved_file.startswith(path) for path in settings.get('search_paths')):
			module_cache.scan_file_for_requires(saved_file)

	# def on_query_completions(self, view, prefix, locations):
	# 	completions = []
	
	# 	if not all(view.score_selector(loc, 'source.js | text.html.basic') for loc in locations):
	# 		return None

	# 	for class_name, module_name in dict(module_cache.modules_by_name).items():
	# 		if class_name.lower().startswith(prefix.lower()):
	# 			completions.append(('%s - %s' % (class_name, module_name[:-len(class_name) - 1]), module_name))
	# 			# completions.append((module_name))

	# 	print 'here', prefix
	# 	print sublime.INHIBIT_WORD_COMPLETIONS
	# 	return (completions, 0)