import DocIcon from '../assets/doc.svg?react';
import BrainIcon from '../assets/brain.svg?react';
import Fade from 'react-bootstrap/Fade';

type LoadingProps = {
    dataLoading: boolean;
    sumLoading: boolean;
    celexData: {
        title: string;
        text: string;
        related_documents: {
            modifies: []; 
            modified_by: [];
          };
      } | null;
  };

function Loading({ dataLoading, sumLoading, celexData }: LoadingProps) {
    console.log(`Loading component rendered with dataLoading: ${dataLoading}, sumLoading: ${sumLoading}`);
    return (
        <div className="main-card px-4 pt-3 my-5 text-center mx-auto d-flex flex-column align-items-center w-75">
            <div className="loading-card shadow p-5 pb-3 rounded-3 text-center w-50">
            <div className="spinner-border load-spin" role="status">
                    <span className="sr-only"></span>
                </div>
                <h3 className="loading-title p-2">Analysing Document</h3>
                <p className="celex-text">Please wait while we process your policy document</p>
                <div className="list-group mt-3">
                        <li className={`${dataLoading ? 'my-active' : 'inactive'} list-group-item rounded mb-2 d-flex align-items-center`}>
                            <div className={`${dataLoading ? 'loading-icon-container-active' : 'loading-icon-container-inactive'}`}>
                        <DocIcon className={`${dataLoading ? 'loading-icon-active' : 'loading-icon-inactive'}`}/>
                        </div>
                            Retrieving CELEX info</li>
                        <li className={`${sumLoading ? 'my-active' : 'inactive'} list-group-item border rounded mb-2 d-flex align-items-center`}>
                        <div className={`${sumLoading ? 'loading-icon-container-active' : 'loading-icon-container-inactive'}`}>
                        <BrainIcon className={`${sumLoading ? 'loading-icon-active' : 'loading-icon-inactive'}`}/>
                        </div>
                            Generating AI summary</li>
                        <div className="preview d-flex px-3 mb-2 justify-content-start">
                            { dataLoading ? 
                            <div className="d-flex flex-column justify-content-start align-items-start w-100 pt-3">
                                <p className="card-text placeholder-glow row w-100 px-2 pb-2">
                                    <span className="placeholder bg-secondary col-9 mb-2 rounded-3"></span>
                                    <span className="placeholder bg-secondary col-6 mb-2 rounded-3"></span>
                                    <span className="placeholder bg-secondary col-7 mb-2 rounded-3"></span>
                                </p>
                            </div>
                            :
                                <div className="mt-4 text-start">
                                    <Fade in={!dataLoading} appear>
                                    <div>
                                        <h6><span className="preview-title">Title:</span> {celexData?.title}</h6>
                                        <p className="text-muted" style={{ maxHeight: '100px', overflow: 'auto' }}>
                                        <span className="fw-semibold">Preview:</span> {celexData?.text?.slice(0, 200)}...
                                        </p>
                                    </div>
                                    </Fade>
                                </div>
                                }
                        </div>
                </div>
                <p className="small celex-text pt-3">This usually takes 30-60 seconds. Thank you for your patience.</p>
            </div>
    </div>
    )
}

export default Loading;