<!-- vscode-markdown-toc -->
* 1. [Development Environment](#DevelopmentEnvironment)
	* 1.1. [uv](#uv)
	* 1.2. [devenv](#devenv)
* 2. [Pull Requests and Commits](#PullRequestsandCommits)
		* 2.1. [Do](#Do)
		* 2.2. [Don't](#Dont)
	* 2.1. [Conventional Commit Rules](#ConventionalCommitRules)
* 3. [Documentation](#Documentation)
* 4. [Concepts](#Concepts)
	* 4.1. [Glossary](#Glossary)
* 5. [Tests](#Tests)
	* 5.1. [Test Style Guidelines](#TestStyleGuidelines)
		* 5.1.1. [File IO](#FileIO)
		* 5.1.2. [Directory structure and file names](#Directorystructureandfilenames)
		* 5.1.3. [Unit tests](#Unittests)
		* 5.1.4. [Integration Tests](#IntegrationTests)
		* 5.1.5. [System tests](#Systemtests)
		* 5.1.6. [Adding new functionalities and tests required](#Addingnewfunctionalitiesandtestsrequired)
		* 5.1.7. [Updating tests](#Updatingtests)
* 6. [Adding a new translatable layer (subject to change)](#Addinganewtranslatablelayersubjecttochange)
	* 6.1. [Ports and automatically combining layers (subject to change)](#Portsandautomaticallycombininglayerssubjecttochange)

<!-- vscode-markdown-toc-config
	numbering=true
	autoSave=true
	/vscode-markdown-toc-config -->
<!-- /vscode-markdown-toc -->
# Contribution Guide
##  1. <a name='DevelopmentEnvironment'></a>Development Environment

###  1.1. <a name='uv'></a>uv

We rely on [uv](https://docs.astral.sh/uv/) to manage the venv and dependencies.
Install uv by following their [install guide](https://docs.astral.sh/uv/getting-started/installation/).
Git clone our repository

```bash
$ git clone https://github.com/es-ude/elastic-ai.creator.git
```

or

```bash
$ git clone git@github.com:es-ude/elastic-ai.creator.git
```

move into the just cloned repository and run

```bash
$ uv sync
```

This install all runtime as well as most of the
development dependencies. There are more (optional)
development dependency groups that you can install,
e.g., the `lsp` group containing 
python-language-server and pylsp-mypy

```bash
$ uv sync --group lsp
```

###  1.2. <a name='devenv'></a>devenv

To share not only python packages for the development environment, but also
other tools we offer a [devenv](https://devenv.sh) configuration.
After installing the nix package manager and [nix](https://nix.dev/install-nix)
and [installing devenv](https://devenv.sh/getting-started/#2-install-devenv) you
can startup a development environment with
```bash
$ devenv shell
```
For more convenience we recommend combining this workflow with direnv for
automatica shell activation as explained [here](https://devenv.sh/automatic-shell-activation/).

Devenv will automatically give you access to all other relevant tools

 * git
 * uv
 * ghdl for hw simulations (run via rosetta on apple silicon)
 * gtkwave for visualizing waveforms produced by ghdl
 * act for testing github workflows locally
 * and more...

for a full list of installed tools have a look at the `devenv.nix` file.


##  2. <a name='PullRequestsandCommits'></a>Pull Requests and Commits
Use conventional commit types especially (`feat`, `fix`) and mark `BREAKING CHANGES`
in commit messages.
Please try to use rebasing and squashing to make sure your commits are atomic.
By atomic we mean, that each commit should make sense on its own.
As an example let's assume you have been working on a new feature `A` and
during that work you were also performing some refactoring and fixed a small
bug that you discovered. Ideally your history would more or less like this:

####  2.1. <a name='Do'></a>Do

```
* feat: introduce A

  Adds several new modules, that enable a new
  workflow using feature A.

  This was necessary because, ...
  This improves ....


* fix: fix a bug where call to function b() would not return

  We only found that now, because there was no test for this
  bug. This commit also adds a new corresponding test.


* refactor: use an adapter to decouple C and D

  This is necessary to allow easier introduction of
  feature A in a later commit.
```

What we want to avoid is a commit history like that one

####  2.2. <a name='Dont'></a>Don't
```
* feat: realize changes requested by reviewer

* feat: finish feature A

* refactor: adjust adapter

* wip: working on feature A

* fix: fix a bug (this time for real)

* fix: fix a bug

* refactor: had to add an adapter

* fix: fix some typos as requested by reviewer

```

If a commit introduces a new feature, 
it should ideally also contain the test coverage, documentation, etc.
If there are changes that are not directly related to that feature, 
they should go into a different commit.

###  2.1. <a name='ConventionalCommitRules'></a>Conventional Commit Rules

We use conventional commits (see [here](https://www.conventionalcommits.org/en/v1.0.0-beta.2/#summary)). The following commit types are allowed. The message scope is optional.


##  3. <a name='Documentation'></a>Documentation
The easiest way to build the documentation yourself is to setup devenv as shown above in the section [devenv](#devenv). Afterwards just run

```bash
$ devenv shell devenv tasks run build:docs
```

After the command has finished you can find the documentation in the `docs/build` folder.

In case you cannot or don't want to setup devenv, you can ensure you have the following dependencies installed:

* pysciidoc
* kramdown-ascii
* asciidoctor-kroki (javascript)
* antora

and run the commands from the 'build:docs' task in the 'devenv.nix' file.


##  4. <a name='Concepts'></a>Concepts
The `elasticai.creator` aims to support
    1. the design and training of hardware optimization aware neural networks
    2. the translation of designs from 1. to a neural network accelerator in a hardware definition language
The first point means that the network architecture, algorithms used during forward as well as backward
propagation strongly depend on the targeted hardware implementation.
Since the tool is aimed at researchers we want the translation process to be straight-forward and easy to reason about.
Opposed to other tools (Apache TVM, FINN, etc.) we prefer flexible prototyping and handwritten
hardware definitions over a wide range of supported architectures and platforms or highly scalable solutions.

The code-base is composed out of the following packages
- `file_generation`:
  - write files to paths on hard disk or to virtual paths (e.g., for testing purposes)
  - simple template definition
  - template writer/expander
- `vhdl`:
  - helper functions to generate frequently used vhdl constructs
  - the `Design` interface to facilitate composition of hardware designs
  - basic vhdl design without a machine learning layer counterpart to be used as dependencies in other designs (e.g., rom modules)
  - additional vhdl designs to make the neural network accelerator accessible via the elasticai.runtime, also see [skeleton](./elasticai/creator/vhdl/system_integrations/README.md)
- `base_modules`:
  - basic machine learning modules that are used as dependencies by translatable layers
- `nn`:
  - package for public layer api; hosting translatable layers of different categories
  - layers within a subpackage of `nn`, e.g. `nn.fixed_point` are supposed to be compatible with each other


###  4.1. <a name='Glossary'></a>Glossary

 - **fxp/Fxp**: prefix for fixed point
 - **flp/Flp**: prefix for floating point
 - **x**: parameter input tensor for layer with single input tensor
 - **y**: output value/tensor for layer with single output
 - **_bits**: suffix to denote the number of bits, e.g. `total_bits`, `frac_bits`, in python context
 - **_width**: suffix to denote the number of bits used for a data bus in vhdl, e.g. `total_width`, `frac_width`
 - **MathOperations/operations**: definition of how to perform mathematical operations (quantization, addition, matrix multiplication, ...)




##  5. <a name='Tests'></a>Tests

Our implementation is tested with unit and integration.
You can run one explicit test with the following statement:

```bash
python3 -m pytest ./tests/path/to/specific/test.py
```

If you want to run all tests, give the path to the tests:

```bash
python3 -m pytest ./tests
```

If you want to add more tests please refer to the Test Guidelines in the following.


###  5.1. <a name='TestStyleGuidelines'></a>Test Style Guidelines

####  5.1.1. <a name='FileIO'></a>File IO

In general try to avoid interaction with the filesystem. In most cases instead of writing to or reading from a file you can use a StringIO object or a StringReader.
If you absolutely have to create files, be sure to use pythons [tempfile](https://docs.python.org/3.9/library/tempfile.html) module and cleanup after the tests.
In most cases you can use the [`InMemoryPath`](elasticai/creator/file_generation/in_memory_path.py) class to write files to the RAM instead of writing them to the hard disc (especially for testing the generated VHDL files of a certain layer).


####  5.1.2. <a name='Directorystructureandfilenames'></a>Directory structure and file names

Files containing tests for a python module should be located in a test directory for the sake of separation of concerns.
Each file in the test directory should contain tests for one and only one class/function defined in the module.
Files containing tests should be named according to the rubric
`test_<class_name>.py`.
Next, if needed for more specific tests define a class. Then subclass it.
It avoids introducing the category of bugs associated with copying and pasting code for reuse.
This class should be named similarly to the file name.
There's a category of bugs that appear if  the initialization parameters defined at the top of the test file are directly used: some tests require the initialization parameters to be changed slightly.
Its possible to define a parameter and have it change in memory as a result of a test.
Subsequent tests will therefore throw errors.
Each class contains methods that implement a test.
These methods are named according to the rubric
`test_<name>_<condition>`


####  5.1.3. <a name='Unittests'></a>Unit tests

In those tests each functionality of each function in the module is tested, it is the entry point  when adding new functions.
It assures that the function behaves correctly independently of others.
Each test has to be fast, so use of heavier libraries is discouraged.
The input used is the minimal one needed to obtain a reproducible output.
Dependencies should be replaced with mocks as needed.

####  5.1.4. <a name='IntegrationTests'></a>Integration Tests

Here the functions' behaviour with other modules is tested.
In this repository each integration function is in the correspondent folder.
Then the integration with a single class of the target, or the minimum amount of classes for a functionality, is tested in each separated file.

####  5.1.5. <a name='Systemtests'></a>System tests

Those tests will use every component of the system, comprising multiple classes.
Those tests include expected use cases and unexpected or stress tests.

####  5.1.6. <a name='Addingnewfunctionalitiesandtestsrequired'></a>Adding new functionalities and tests required

When adding new functions to an existing module, add unit tests in the correspondent file in the same order of the module, if a new module is created a new file should be created.
When a bug is solved created the respective regression test to ensure that it will not return.
Proceed similarly with integration tests.
Creating a new file if a functionality completely different from the others is created e.g. support for a new layer.
System tests are added if support for a new library is added.

####  5.1.7. <a name='Updatingtests'></a>Updating tests

If new functionalities are changed or removed the tests are expected to reflect that, generally the ordering is unit tests -> integration tests-> system tests.
Also, unit tests that change the dependencies should be checked, since this system is fairly small the internal dependencies are not always mocked.

references: https://jrsmith3.github.io/python-testing-style-guidelines.html

##  6. <a name='Addinganewtranslatablelayersubjecttochange'></a>Adding a new translatable layer (subject to change)

Adding a new layer involves three main tasks:
1. define the new ml framework module, typically you want to inherit from `pytorch.nn.Module` and optionally use one
        of our layers from `base_module`
   - this specifies the forward and backward pass behavior of your layer
2. define a corresponding `Design` class
   - this specifies
     - the hardware implementation (i.e., which files are written to where and what's their content)
     - the interface (`Port`) of the design, so we can automatically combine it with other designs
     - to help with the implementation, you can use the template system as well as the `elasticai.creator.vhdl.code_generation` modules
3. define a trainable `DesignCreator`, typically inheriting from the class defined in 1. and implement the `create_design` method which
   a. extracts information from the module defined in 1.
   b. converts that information to native python types
   c. instantiates the corresponding design from 2. providing the necessary data from a.
    - this step might involve calling `create_design` on submodules and inject them into the design from 2.


###  6.1. <a name='Portsandautomaticallycombininglayerssubjecttochange'></a>Ports and automatically combining layers (subject to change)
The algorithm for combining layers lives in `elasticai.creator.vhdl.auto_wire_protocols`.
Currently, we support two types of interfaces: a) bufferless design, b) buffered design.

b) a design that features its own buffer to store computation results and will fetch its input data from a previous buffer
c) a design without buffer that processes data as a stream, this is assumed to be fast enough such that a buffered design can fetch its input data through a bufferless design

The *autowiring algorithm* will take care of generating vhdl code to correctly connect a graph of buffered and bufferless designs.

A bufferless design features the following signals:

| name |direction | type           | meaning                                         |
|------|----------|----------------|-------------------------------------------------|
| x    | in       |std_logic_vector| input data for this layer                       |
| y    | out      |std_logic_vector| output data of this layer                       |
| clock| in       |std_logic       | clock signal, possibly shared with other layers |


For a buffered design we define the following signals:

| name |direction | type           | meaning                                         |
|------|----------|----------------|-------------------------------------------------|
| x    | in       |std_logic_vector| input data for this layer                       |
| x_address | out | std_logic_vector | used by this layer to address the previous buffer and fetch data, we address per input data point (this typically corresponds to the number of input features) |
| y    | out      |std_logic_vector| output data of this layer                       |
| y_address | in  | std_logic_vector | used by the following buffered layer to address this layers output buffer (connected to the following layers x_address). |
| clock| in       |std_logic       | clock signal, possibly shared with other layers |
|done | out | std_logic | set to "1" when computation is finished |
|enable | in | std_logic | compute while set to "1" |
