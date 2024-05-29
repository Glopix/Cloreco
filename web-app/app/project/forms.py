from flask_wtf import FlaskForm, Form
from wtforms import StringField, SubmitField, FieldList, FormField, SelectField, TextAreaField, FileField
from wtforms.validators import DataRequired
from project.settings import ImageBuilder

class NewToolArgumentsForm(Form):
    """Subform.

    Arguments, descriptions and default values for the new, to be added clone detector tool can be set via this form.

    CSRF is disabled for this subform (using 'Form' as parent class) because
    it is never used by itself.

    uppercase variable identifiers, because 'name' and 'description' would interfere with the identifiers of flask_wtf
    """
    Name =          StringField('Name', default="", validators=[DataRequired()],
                                description="Identifier of your tools arguments")
    Description =   TextAreaField('Description', 
                                  description="""Description of your tools arguments. These descriptions will be displayed in the 'run' page.
                    ("<br>" tags or newline(enter) can be used for linebreaks)""")
    DefaultValue =  StringField('Default value (optional)', 
                                description="Default values of each arguments.")

class BenchmarkDefaultValuesForm(Form):
    """Subform.

    Default values for the Benchmark arguments can be set via this form.

    CSRF is disabled for this subform (using 'Form' as parent class) because
    it is never used by itself.

    uppercase variable identifiers, because 'name' and 'description' would interfere with the identifiers of flask_wtf
    """
    argument = StringField('', default="", description="" )

class GitRepoToolForm(Form):
    """Subform.

    general information about the clone detector tool,
    with informations necessary to add create a image of this clone detector tool, based on a git repistory

    """
    toolName =  StringField('Clone detector tool name', 
                    description="this name will be displayed in the web form" ,
                    validators=[DataRequired()]
                )

    gitRepoURL = StringField( 'Repository URL',
                    description="remote repository URL, where the clone detector tool is stored",
                    validators=[DataRequired()]
                )
       
    jdkVersion = SelectField('JDK Version',
                    description="which Java Development Kit(JDK) version your tool needs",
                    choices=[(choice, choice) for choice in ImageBuilder['availableJDKs']],
                    validators=[DataRequired()]
                )
    
    distro =     SelectField('Distribution',
                    description="""which Distribution to build on <br> 
                    Please note: not every software which is installed on the full distribution 
                    (e.g. ubuntu 22.04) is pre-installed in its docker image version. 
                    Make sure every dependency of your tool is installed via the 'install.sh' script, 
                    provided in your specified Git repository""",
                    choices=[(choice, choice) for choice in ImageBuilder['availableDistros']],
                    validators=[DataRequired()]
                )
    
    installDir = StringField( 'Installation directory',
                    description="""Your clone detector tool will be installed in this path. <br>
                                    Enter an absolute path. <br>
                                    Recommended: /cloneDetection/Applications/<tool name>/ <br>
                                    e.g.: /cloneDetection/Applications/MyNewTool/
                                    """,
                    validators=[DataRequired()]
                )

class ImageToolForm(Form):
    """Subform.

    general information about the clone detector tool,
    with informations necessary to add the tool from a image

    """    
    toolName           = StringField('Clone detector tool name', 
                            description="this name will be displayed in the web form" ,
                            validators=[DataRequired()]
                        )

    # docker only
    toolConfigFilePath = StringField('tool config file Path',
                            description="""the configuration file for your new clone detector tool will be saved there. 
                            Please make sure that your clone detector tool reads its configurations from this path. 
                            Enter an absolute path.""",
                            validators=[DataRequired()]
                        )
    
    imageURL           = StringField( 'Image URL',
                            description="""remote image URL, where the clone detector tool is stored in a (docker) image, e.g.: <br> 
                            ghcr.io/glopix/cloreco-images/stone-detector:latest """,
                            validators=[DataRequired()]
                        )

class GitRepoForm(FlaskForm):
    tool = FormField(GitRepoToolForm)
    submit = SubmitField('Submit')

class ImageForm(FlaskForm):
    tool = FormField(ImageToolForm)
    # Dynamic list of field items
    toolArgs = FieldList(
                    FormField(NewToolArgumentsForm), 
                    min_entries=1,
                )
    toolArgsFile = FileField('Tool arguments file in shell-style') # optional

    benchmarkArgs = FieldList(
                    FormField(BenchmarkDefaultValuesForm),
                )

    submit = SubmitField('Submit')
