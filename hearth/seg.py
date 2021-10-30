import os
from typing import Union
from . import utils

__all__ = ["get_resample_aseg_cmd", "get_generate_dicom_seg_cmd"]


def get_resample_aseg_cmd(
    aseg_image_file: Union[str, bytes, os.PathLike],
    t1_dicom_file: Union[str, bytes, os.PathLike],
    resampled_aseg: Union[str, bytes, os.PathLike],
) -> str:
    """Generate the command string to resample the aseg to the T1w DICOM space

    TODO: remove FreeSurfer requirement, using nibabel or other tool

    Parameters
    ----------
    aseg_image_file : Union[str, bytes, os.PathLike]
        Path to the FreeSurfer aseg.mgz file
    t1_dicom_file : Union[str, bytes, os.PathLike]
        Path to a T1w DICOM file
    resampled_aseg : Union[str, bytes, os.PathLike]
        Output path for the resampled aseg.mgz

    Returns
    -------
    str
        mri_vol2vol command to move the aseg.mgz to the T1w DICOM space
    """
    command = (
        "mri_vol2vol "
        f"--mov {aseg_image_file} "
        f"--targ {t1_dicom_file} "
        "--regheader --nearest "
        f"--o {resampled_aseg}"
    )
    return command


def get_generate_dicom_seg_cmd(
    resampled_aseg: Union[str, bytes, os.PathLike],
    aseg_dicom_seg_metadata: Union[str, bytes, os.PathLike],
    t1_dicom_file: Union[str, bytes, os.PathLike],
    aseg_dicom_seg_output: Union[str, bytes, os.PathLike],
) -> str:
    """Generate the command to create a DICOM SEG image using dcmqi

    Parameters
    ----------
    resampled_aseg : Union[str, bytes, os.PathLike]
        aseg.mgz resampled to the T1w DICOM space
    aseg_dicom_seg_metadata : Union[str, bytes, os.PathLike]
        The metadata schema relating the aseg.mgz to anatomic labels used in DICOM
    t1_dicom_file : Union[str, bytes, os.PathLike]
        Path to a T1w DICOM file
    aseg_dicom_seg_output : Union[str, bytes, os.PathLike]
        Output path for the DICOM seg

    Returns
    -------
    str
        itkimage2segimage (from dcmqi) command to create a DICOM SEG from the aseg.mgz in T1w DICOM space
    """
    t1_dicom_dir = utils.abs_dirname(t1_dicom_file)
    command = (
        "itkimage2segimage "
        f"--inputDICOMDirectory {t1_dicom_dir} "
        f"--inputMetadata {aseg_dicom_seg_metadata} "
        f"--inputImageList {resampled_aseg} "
        f"--outputDICOM {aseg_dicom_seg_output} "
        "--skip"
    )
    return command
