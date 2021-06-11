## Based on: https://github.com/timothycrosley/pdocs/blob/c122cdf873aad4fa131bc7ed968da3dd393df43b/pdocs/templates/text.mako

## Define mini-templates for each portion of the doco.

<%def name="h1(s)"># ${s}
</%def>
<%def name="h2(s)">## ${s}
</%def>
<%def name="h3(s)">### ${s}
</%def>
<%def name="h4(s)">#### ${s}
</%def>
<%def name="par(s)">
% if s:
${s}

% endif
</%def>
<%def name="folded_code(source)">
% if show_source_code and source:

??? example "View Source"
    ```python3
    ${"    ".join(source)}
    ```

% endif
</%def>

## Define Larger templates

<%def name="function(func, class_level=False)" buffered="True">
    <%
        returns = func.return_annotation()
        if returns:
            returns = ' -> ' + returns
        parsed_ds = func.parsed_docstring
    %>
% if class_level:
${h4(func.name)}
% else:
${h3(func.name)}
% endif

```python3
%if func.params():
def ${func.name}(
    ${",\n    ".join(func.params())}
)${returns}
% else:
def ${func.name}()${returns}
% endif
```

% if parsed_ds:
    <%
        short_desc = parsed_ds.short_description
        long_desc = parsed_ds.long_description
        params = parsed_ds.params
        ret = parsed_ds.returns
        raises = parsed_ds.raises
    %>
${par(short_desc)}
${par(long_desc)}

    % if params:
**Parameters:**

| Name | Description |
|---|---|
        % for p in params:
| ${p.arg_name} | ${p.description.replace('\n', '<br>')} |
        % endfor
    % endif

    % if ret:

**${"Yields:" if ret.is_generator else "Returns:"}**

| Type | Description |
|---|---|
## PLANNED: handle multiline descriptions
| ${ret.type_name} | ${ret.description} |
    % endif
    % if raises:

**Raises:**

| Type | Description |
|---|---|
        % for r in raises:
## PLANNED: handle multiline descriptions
| ${r.type_name} | ${r.description} |
        % endfor
    % endif
% else:
${func.docstring}
% endif

${folded_code(func.source)}
</%def>

<%def name="variable(var)" buffered="True">
```python3
${var.name}
```
<%
    var_pd = var.parsed_docstring
    if var_pd:
        short_desc = var_pd.short_description
        long_desc = var_pd.long_description
%>
% if var_pd:
${par(short_desc)}
${par(long_desc)}
% else:
${var.docstring}
% endif

</%def>

<%def name="class_(cls)" buffered="True">
${h3(cls.name)}

```python3
class ${cls.name}(
    ${",\n    ".join(cls.params())}
)
```

% if cls.parsed_docstring:
    % if cls.parsed_docstring.params:
${h4("Attributes")}

| Name | Description |
|---|---|
        % for p in cls.parsed_docstring.params:
| ${p.arg_name} | ${p.description.replace('\n', '<br>')} |
        % endfor
    % endif
% else:
${cls.docstring}
% endif

${folded_code(cls.source)}

<%
  class_vars = cls.class_variables()
  static_methods = cls.functions()
  inst_vars = cls.instance_variables()
  methods = cls.methods()
  mro = cls.mro()
  subclasses = cls.subclasses()
%>
% if mro:
${h4('Ancestors (in MRO)')}
    % for c in mro:
* ${c.refname}
    % endfor
% endif

% if subclasses:
${h4('Descendants')}
    % for c in subclasses:
* ${c.refname}
    % endfor
% endif

% if class_vars:
${h4('Class variables')}
    % for v in class_vars:
${variable(v)}

    % endfor
% endif

% if static_methods:
${h4('Static methods')}
    % for f in static_methods:
${function(f, True)}

    % endfor
% endif

% if inst_vars:
${h4('Instance variables')}
% for v in inst_vars:
${variable(v)}

% endfor
% endif
% if methods:
${h4('Methods')}
% for m in methods:
${function(m, True)}

% endfor
% endif

</%def>

## Start the output logic for an entire module.

<%
  variables = module.variables()
  classes = module.classes()
  functions = module.functions()
  submodules = module.submodules
  heading = 'Namespace' if module.is_namespace else ''
  parsed_ds = module.parsed_docstring
%>

${h1(heading + " " + module.name)}
% if parsed_ds:
${par(parsed_ds.short_description)}
${par(parsed_ds.long_description)}
## PLANNED: add meta (example and notes)
% else:
${module.docstring}
% endif

${folded_code(module.source)}

% if submodules:
${h2("Sub-modules")}
    % for m in submodules:
* [${m.name}](${m.name.split(".")[-1]}/)
    % endfor
% endif

% if variables:
${h2("Variables")}
    % for v in variables:
${variable(v)}

    % endfor
% endif

% if functions:
${h2("Functions")}
    % for f in functions:
${function(f)}

    % endfor
% endif

% if classes:
${h2("Classes")}
    % for c in classes:
${class_(c)}

    % endfor
% endif
